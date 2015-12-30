# -*- coding: utf-8 -*-
import curses
import locale
import time
import math
import sys
from util.util import bearing_to_angle, angle_to_bearing

from util.point import Point


class GameCoursesInterface(object):
    def __init__(self, sea, player_sub):
        self.player_sub = player_sub
        self.sea = sea
        self.time_rate = 1  # 1 time(s) faster
        self.update_rate = 0.1  # updates every 0.1 second
        self.display_screen = ''

        # setlocale enables UTF chars
        # see: https://docs.python.org/2/library/curses.html
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.strcode = locale.getpreferredencoding()
        screen = curses.initscr()
        self.screen = screen
        screen.nodelay(1)
        curses.noecho()
        curses.curs_set(0)
        screen.keypad(1)

        curses.start_color()
        curses.use_default_colors()

    def angles_to_unicode(self, angle):
        def interval(a, direction):
            return direction-22.5 <= a < direction+22.5

        if angle is None:
            return u'\u2219'.encode(self.strcode)
        elif interval(angle, 45):
            return u'\u2197'.encode(self.strcode)
        elif interval(angle, 90):
            return u'\u2192'.encode(self.strcode)
        elif interval(angle, 135):
            return u'\u2198'.encode(self.strcode)
        elif interval(angle, 180):
            return u'\u2193'.encode(self.strcode)
        elif interval(angle, 225):
            return u'\u2199'.encode(self.strcode)
        elif interval(angle, 270):
            return u'\u2190'.encode(self.strcode)
        elif interval(angle, 315):
            return u'\u2196'.encode(self.strcode)
        else:
            return u'\u2191'.encode(self.strcode)

    def speed_up(self):
        s = self.time_rate
        if s < 20:
            s += 1
        elif s >= 20:
            s = 20
        self.time_rate = s

    def speed_down(self):
        s = self.time_rate
        if s > 0:
            s -= 1
        self.time_rate = s

    def msg(self, text):
        # self.screen.addstr(8, 0, " "*30)
        self.screen.addstr(11, 0, text)
        # self.screen.clrtoeol()


    def update_time(self):
        self.sea.turn(self.time_rate * self.update_rate / 3600)  # sea turn runs in hours

    def f_to_text(self,value, mask='{:2.1f}'):
        if value is None:
            return "-"
        else:
            return mask.format(value)

    def update_screen(self):
        s = self.screen
        for i in range(3,11):
            s.move(i,0)
            s.clrtoeol()
        #s.clear()
        sub = self.player_sub

        s.addstr(0, 0, "{sea} (time rate: {tr}x)".format(sea=self.sea, tr=self.time_rate))
        s.clrtoeol()

        s.addstr(1, 0, "pos:{pos} dest:{dest} spd:{spd:2.1f} ({sspd}) deep:{deep:.0f} ({sdeep})".format(
                                                                        pos=sub.position,
                                                                        dest=self.f_to_text(sub.nav.destination,mask='{}'),
                                                                        spd=self.player_sub.speed,
                                                                        sspd=self.f_to_text(self.player_sub.nav.speed),
                                                                        deep=self.player_sub.actual_deep,
                                                                        sdeep=self.player_sub.set_deep))
        s.clrtoeol()

        if self.display_screen == 'n':
            self.screen.addstr(3, 00, 'Current')
            self.screen.addstr(3, 40, 'Navigation')

            self.screen.addstr(4, 00, 'Position: {pos}'.format(pos=sub.position))
            self.screen.addstr(4, 40, '{pos}'.format(pos=sub.nav.destination))

            self.screen.addstr(5, 00, 'Course  : {:03.1f}{}'.format(sub.bearing, self.angles_to_unicode(sub.bearing)))  # angles_to_unicode(sub.bearing)
            if sub.nav.destination is not None:
                self.screen.addstr(5, 40, '{:03.1f}{} deg'.format(angle_to_bearing(sub.nav.angle_to_destination), self.angles_to_unicode(angle_to_bearing(sub.nav.angle_to_destination))))

            self.screen.addstr(6, 00, 'Speed   : {:2.1f} knots (turbine {:3.1f}%)'.format(sub.speed, sub.turbine.level))

            if sub.nav.speed is None:
                set_speed = '-'
            else:
                set_speed = '{:2.1f} knots'.format(sub.nav.speed)
                # set_speed = '{:2.1f} knots (turbine {:3.1f}%)'.format(sub.nav.speed, sub.nav.turbine_level_needed)

            self.screen.addstr(6, 40, set_speed)
            # self.screen.addstr(6, 40, '{:2.1f} knots (turbine {:3.1f}%)'.format(sub.nav.speed, sub.nav.turbine_level_needed))

            # self.screen.addstr(6, 30, 'Speed   : {:2.1f} knots'.format(sub.speed))
            self.screen.addstr(7, 00, 'Rudder  : {:0.0f} deg/min'.format(math.degrees(sub.rudder/60)))

        elif self.display_screen == 's':
            self.screen.addstr(3, 00, 'Passive Sonar')


        elif self.display_screen == 'M':
            self.screen.addstr(3, 00, 'Turbine power: {:3.1f}%'.format(sub.turbine.level))
            self.screen.addstr(3, 30, 'Turbine acc  : {} -> {:2.3f} Knots/s'.format(sub.turbine_acceleration/3600,sub.turbine_acceleration.length/3600))

            self.screen.addstr(4, 00, 'Drag factor  : {:2.2f}'.format(sub.drag_factor))
            self.screen.addstr(4, 30, 'Drag acc     : {} -> {:2.3f} Knots/s'.format(sub.drag_force/3600,sub.drag_force.length/-3600.0))

            self.screen.addstr(5, 00, 'Speed        : {} => {:2.1f} Knots'.format(sub._velocity, sub.speed ))

            self.screen.addstr(6, 00, 'Acceleration : {} => {:2.3f} Knots/s'.format(sub._acceleration/3600, abs(sub._acceleration/3600) ))

            self.screen.addstr(7, 00, 'Ship bearing : {:2.3f}'.format(math.degrees(sub.ship_bearing)))
            self.screen.addstr(7, 30, 'Vel. bearing : {:2.3f}'.format(math.degrees(sub.course)))
            self.screen.addstr(7, 60, 'diff : {:2.3f}'.format(math.degrees(sub.course - sub.ship_bearing)))

            self.screen.addstr(8, 00, 'Rudder : {} deg/min'.format(math.degrees(sub.rudder/60)))

            self.screen.addstr(9, 00, 'Nav Acc.     : {:3.5f} knots/s'.format(sub.nav.acceleration_needed/3600))
            self.screen.addstr(9, 40, 'Nav Turbine  : {:3.1f}%'.format(sub.nav.turbine_level_needed))

        elif self.display_screen == 'N':

            self.screen.addstr(3, 00, 'Speed        : {} => {:2.1f} Knots'.format(sub._velocity, sub.speed ))
            self.screen.addstr(4, 00, 'Ship bearing : {:2.3f}'.format(math.degrees(sub.ship_bearing)))
            self.screen.addstr(4, 30, 'Vel. bearing : {:2.3f}'.format(math.degrees(sub.course)))
            self.screen.addstr(4, 60, 'diff : {:2.3f}'.format(math.degrees(sub.course - sub.ship_bearing)))
            self.screen.addstr(5, 00, 'Rudder : {:2.3f} deg/min'.format(math.degrees(sub.rudder/60)))

            self.screen.addstr(6, 00, 'Angle to destination : {:2.3f} deg'.format(math.degrees(sub.nav.angle_to_destination)))
            self.screen.addstr(6, 40, 'Angle difference : {:2.3f} deg'.format(math.degrees(sub.nav.angle_difference)))



        else:
            self.screen.addstr(3, 0, 'n - navigation')
            self.screen.addstr(4, 0, 's - sonar')
            self.screen.addstr(5, 0, 'r - radar')
            self.screen.addstr(6, 0, 'w - weapons')

        s.refresh()

    def parse_coordinates(self, text):
        try:
            coord = text.split(',')
            if len(coord) != 2:
                return None
            x = float(coord[0])
            y = float(coord[1])
            return Point(x, y)
        except ValueError:
            return None

    def get_command(self):
        line = 11
        s = self.screen
        s.addstr(line, 0, " " * 30)
        s.nodelay(0)
        curses.echo()
        s.addstr(line, 0, "->")
        s.clrtoeol()
        command = s.getstr(line, 3)
        curses.noecho()
        s.nodelay(1)
        s.addstr(line, 0, " " * 30)
        return command

    def command(self):
        c = self.get_command()
        sub = self.player_sub
        if c.strip() == '':
            return

        opt = c.split(' ')

        if opt[0] == 'mov':
            destination = self.parse_coordinates(opt[1])
            if destination:
                sub.nav.destination = destination
                self.msg("Aye, aye! Destination set to {0}, captain!".format(self.player_sub.nav.destination))
            else:
                self.msg("Invalid input")

        if opt[0] == 'spd':
            if len(opt) == 2:
                n = int(opt[1])
                sub.nav.speed = n
                self.msg("Changing speed to {0}".format(sub.nav.speed))

        if opt[0] == 'turbine' and len(opt) == 2:
            n = int(opt[1])
            sub.nav.speed = None
            sub.turbine.level = n
            self.msg("Changing turbine level to {0}%".format(sub.turbine.level))

        if opt[0] == 'rudder' and len(opt) == 2:
            n = int(opt[1]) # degrees per minute
            sub.nav.set_manual()
            sub.rudder = math.radians(n)*60 # *60 because rudder is in degrees per hour
            self.msg("Changing rudder to {0} degrees per minute".format(math.degrees(sub.rudder)/60))

        if opt[0] == 'deep' and len(opt) == 2:
            n = int(opt[1])
            sub.set_deep = n
            self.msg("Changing deep to {0}".format(sub.set_deep))

    def run(self):
        s = self.screen
        while 1:
            k = s.getch()
            if k != curses.ERR:
                # curses.flash()
                # s.addstr(0, 0, chr(k))
                if k == ord('q'):
                    break
                elif k == ord(' '):
                    self.command()

                # Speeds
                elif k == ord('+') or k == ord('='):
                    self.speed_up()
                elif k == ord('-'):
                    self.speed_down()

                # screens
                # elif k == ord('n'):
                #     self.display_screen = 'n'
                # elif k == ord('N'):
                #     self.display_screen = 'N'
                # elif k == ord('r') or k == ord('R'):
                #     self.display_screen = 'r'
                # elif k == ord('s') or k == ord('S'):
                #     self.display_screen = 's'
                # elif k == ord('w') or k == ord('W'):
                #     self.display_screen = 'w'
                else:
                    try:
                        self.display_screen = chr(k)
                    except:
                        pass

            time.sleep(self.update_rate)
            self.update_time()
            self.update_screen()

        # ends and closes interface
        curses.nocbreak()
        s.keypad(0)
        curses.echo(1)
        curses.endwin()





