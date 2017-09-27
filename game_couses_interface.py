# -*- coding: utf-8 -*-
import curses
import locale
import time
import math
import sys
from util.util import bearing_to_angle, angle_to_bearing
from util.linear_scale import linear_scaler
from util.point import Point


class GameCoursesInterface(object):
    COMMAND_LINE = 12

    def __init__(self, player_sub):
        self.player_sub = player_sub
        # self.sea = sea
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


    def f_to_text(self,value, mask='{:2.1f}'):
        if value is None:
            return "-"
        else:
            return mask.format(value)

    def render(self):
        s = self.screen
        for i in range(3,11):
            s.move(i,0)
            s.clrtoeol()
        #s.clear()
        sub = self.player_sub

        # s.addstr(0, 0, "{sea} (time rate: {tr}x)".format(sea=self.sea, tr=self.time_rate))
        s.clrtoeol()

        # s.addstr(1, 0, "pos:{pos} dest:{dest} spd:{spd:2.1f} ({sspd}) deep:{deep:.0f} ({sdeep})".format(
        #                                                                 pos=sub.position,
        #                                                                 dest=self.f_to_text(sub.nav.destination,mask='{}'),
        #                                                                 spd=self.player_sub.speed,
        #                                                                 sspd=self.f_to_text(self.player_sub.nav.speed),
        #                                                                 deep=self.player_sub.actual_deep,
        #                                                                 sdeep=self.player_sub.target_deep))
        s.clrtoeol()

        if self.display_screen == 'n':
            self.screen.addstr(3, 00, 'Current')
            self.screen.addstr(3, 40, 'Target')

            self.screen.addstr(4, 00, 'Position: {pos}'.format(pos=sub.position))
            # self.screen.addstr(4, 40, '{pos}'.format(pos=sub.nav.destination))

            # self.screen.addstr(5, 00, 'Course  : {:03.1f}{}'.format(sub.course, self.angles_to_unicode(sub.course)))  # angles_to_unicode(sub.bearing)
            # if sub.nav.destination is not None:
            #     self.screen.addstr(5, 40, '{:03.1f}{} deg'.format(angle_to_bearing(sub.nav.angle_to_destination), self.angles_to_unicode(angle_to_bearing(sub.nav.angle_to_destination))))

            self.screen.addstr(6, 00, 'Speed   : {:2.1f} knots (turbine {:3.1f}%)'.format(sub.actual_speed, sub.turbine_level))

            if sub.target_speed is None:
                target_speed = '-'
            else:
                # set_speed = '{:2.1f} knots'.format(sub.target_speed)
                target_speed = '{:2.1f} knots (turbine {:3.1f}%)'.format(sub.target_speed, sub.turbine_level_needed)

            self.screen.addstr(6, 40, target_speed)

            # self.screen.addstr(6, 30, 'Speed   : {:2.1f} knots'.format(sub.speed))
            self.screen.addstr(7, 00, 'Rudder  : {:0.0f} deg/min'.format(math.degrees(sub.rudder/60)))

        elif self.display_screen == 's':
            self.screen.addstr(3, 00, 'Passive Sonar')


        elif self.display_screen == 'k':
            for i in range(3,12):
                self.screen.addstr(i, 00, 'line '+str(i))


        elif self.display_screen == 'M':
            row = 3

            self.screen.addstr(row, 00, 'Time Elapsed: {:3.10f} seconds, {:3.10f} hours'.format(sub.time_elapsed * 3600, sub.time_elapsed))
            row += 1

            self.screen.addstr(row, 00, 'Actual Speed : {:2.1f} Knots'.format(sub.actual_speed ))
            self.screen.addstr(row, 30, 'Target Speed : {:2.1f} Knots'.format(sub.target_speed ))
            row += 1

            self.screen.addstr(row, 00, 'Turbine level: {:3.1f}%'.format(sub.turbine_level))
            self.screen.addstr(row, 30, 'Turbine acc  : {} -> {:2.3f} Knots/s'.format(sub.turbine_acceleration, sub.turbine_acceleration.length))

            row += 1

            self.screen.addstr(row, 00, 'Turb. Needed : {:3.1f}'.format(sub.turbine_level_needed))
            # self.acceleration_needed = self.DRAG_FACTOR * (self.target_speed**2)
            # self.turbine_level_needed = 100.0 * self.acceleration_needed / self.MAX_ACCELERATION


            row += 1
            self.screen.addstr(row, 00, 'Drag factor  : {:2.2f}'.format(sub.DRAG_FACTOR))
            self.screen.addstr(row, 30, 'Actual Drag  : {:2.3f}'.format(sub.drag_factor))
            row += 1


            self.screen.addstr(row, 00, 'Total Drag A : {:2.2f}'.format(sub.total_drag_acceleration))
            self.screen.addstr(row, 30, 'Drag acc     : {} -> {:2.3f} Knots/s'.format(sub.drag_acceleration,sub.drag_acceleration.length))
            row += 2

            self.screen.addstr(row, 00, 'Sub Accel.    : {} => {:2.3f} Knots/s'.format(sub._acceleration, abs(sub._acceleration) ))
            self.screen.addstr(row, 30, 'Accel. Needed : {:2.3f} => {:2.3f} Knots/s'.format(sub.acceleration_needed, abs(sub._acceleration) ))
            row += 1

            self.screen.addstr(row, 00, 'Sub Velocity : {} => {:2.1f} Knots'.format(sub._velocity, sub._velocity.length ))
            row += 1
            self.screen.addstr(row, 00, 'Sub Position : {}'.format(sub._position ))
            row += 1

            self.screen.addstr(7, 00, 'Ship bearing : {:2.3f}'.format(math.degrees(sub._ship_course)))
            self.screen.addstr(row, 30, 'Vel. bearing : {:2.3f}'.format(math.degrees(sub._velocity.get_angle())))
            self.screen.addstr(7, 70, 'diff : {:2.3f}'.format(math.degrees(sub._ship_course - sub._velocity.get_angle())))
            row += 1

            self.screen.addstr(row, 00, 'Rudder : {} deg/min'.format(math.degrees(sub.rudder/60)))


        elif self.display_screen == 'N':

            self.screen.addstr(3, 00, 'Speed        : {} => {:2.1f} Knots'.format(sub.actual_speed, sub.target_speed ))
            self.screen.addstr(4, 00, 'Ship bearing : {:2.3f}'.format(math.degrees(sub.course)))
            self.screen.addstr(4, 30, 'Vel. bearing : {:2.3f}'.format(math.degrees(sub._velocity.get_angle())))
            self.screen.addstr(4, 60, 'diff : {:2.3f}'.format(math.degrees(sub.course - sub._velocity.get_angle())))
            self.screen.addstr(5, 00, 'Rudder : {:2.3f} deg/min'.format(math.degrees(sub.rudder/60)))

            # self.screen.addstr(6, 00, 'Angle to destination : {:2.3f} deg'.format(math.degrees(sub.nav.angle_to_destination)))
            # self.screen.addstr(6, 40, 'Angle difference : {:2.3f} deg'.format(math.degrees(sub.nav.angle_difference)))


        elif self.display_screen == 'e':
            self_noise = self.player_sub.get_self_noise()
            sea_noise =  self.player_sub.get_sea_noise()

            # l1, l2 = sea_noise.ascii2lines(linear_scaler([0,160],[0,16]))

            self.screen.addstr(3, 00, 'Sea conditions            : {}, {}   '.format( self.sea.sea_state_description(), "raining" if self.sea.raining else "no rain" ))
            self.screen.addstr(4, 00, 'Sea noise at {:3.0f} feet deep: {:.1f} db'.format(self.player_sub.actual_deep,sea_noise.total_decibels()))
            self.screen.addstr(4, 60, '{}'.format(sea_noise.ascii()))

            # self.screen.addstr(6, 60, '{}'.format(l2))
            # self.screen.addstr(7, 60, '{}'.format(l1))


            self.screen.addstr(9, 00, 'Submarine self noise : {:.1f} db'.format(self_noise.total_decibels()))
            self.screen.addstr(9, 60, '{}'.format(self_noise.ascii()))

        else:
            self.screen.addstr(3, 0, 'n - navigation')
            self.screen.addstr(4, 0, 's - sonar')
            self.screen.addstr(5, 0, 'r - radar')
            self.screen.addstr(6, 0, 'w - weapons')
            self.screen.addstr(7, 0, 'e - enviroment')

        # s.move(i, 0)
        # s.clrtoeol()


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
        s = self.screen
        s.move(self.COMMAND_LINE, 0)
        s.clrtoeol()
        s.nodelay(0)
        curses.echo()
        s.addstr(self.COMMAND_LINE, 0, "->")
        s.clrtoeol()
        command = s.getstr(self.COMMAND_LINE, 3)
        curses.noecho()
        s.nodelay(1)
        s.move(self.COMMAND_LINE, 0)
        s.clrtoeol()
        # s.addstr(self.COMMAND_LINE, 0, " " * 30)
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
                sub.destination = destination
                # self.msg("Aye, aye! Destination set to {0}, captain!".format(self.player_sub.nav.destination))
            else:
                self.msg("Invalid input")

        if opt[0] == 'speed' or opt[0] == 'spd' or opt[0] == 's':
            if len(opt) == 2:
                n = int(opt[1])
                sub.target_speed = n
                self.msg("Changing speed to {0}".format(sub.target_speed))

        if opt[0] == 'turbine' and len(opt) == 2:
            n = int(opt[1])
            # sub.nav.speed = None
            sub.turbine.level = n
            self.msg("Changing turbine level to {0}%".format(sub.turbine.level))

        if opt[0] == 'rudder' and len(opt) == 2:
            n = int(opt[1]) # degrees per minute
            # sub.nav.set_manual()
            sub.rudder = math.radians(n)*60 # *60 because rudder is in degrees per hour
            self.msg("Changing rudder to {0} degrees per minute".format(math.degrees(sub.rudder)/60))

        if opt[0] == 'deep' and len(opt) == 2:
            n = int(opt[1])
            sub.set_deep = n
            self.msg("Changing deep to {0}".format(sub.set_deep))

    def read_keyboard(self):
        s = self.screen
        k = s.getch()
        if k != curses.ERR:
            # curses.flash()
            # s.addstr(0, 0, chr(k))
            if k == ord('q'):
                self.finalize()
                exit()
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


    def finalize(self):
        # ends and closes interface
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo(1)
        curses.endwin()





