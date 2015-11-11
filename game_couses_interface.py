# -*- coding: utf-8 -*-
import curses
import locale
import time
import sys
from util import angles_to_unicode



from physic import Point

class GameCoursesInterface(object):
    def __init__(self, sea, player_sub):
        self.player_sub = player_sub
        self.sea = sea
        self.time_rate = 1  # 1 time(s) faster
        self.update_rate = 0.1  # updates every 0.1 second
        self.display_screen = ''

        # setlocale enables UTF chars
        # see: https://docs.python.org/2/library/curses.html
        locale.setlocale(locale.LC_ALL, '')
        screen = curses.initscr()
        self.screen = screen
        screen.nodelay(1)
        curses.noecho()
        curses.curs_set(0)
        screen.keypad(1)

        curses.start_color()
        curses.use_default_colors()

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
        self.screen.addstr(8, 0, text)
        self.screen.clrtoeol()


    def update_time(self):
        self.sea.turn(self.time_rate * self.update_rate / 3600)  # sea turn runs in hours

    def update_screen(self):
        s = self.screen
        nav = self.player_sub.nav

        s.addstr(0, 0, "{sea} (time rate: {tr}x)".format(sea=self.sea, tr=self.time_rate))
        s.clrtoeol()

        s.addstr(1, 0, "{nav} deep:{deep:.0f} (set:{sdeep})".format(nav=self.player_sub.nav,
                                                                        deep=self.player_sub.actual_deep,
                                                                        sdeep=self.player_sub.set_deep))
        s.clrtoeol()

        if self.display_screen == 'n':
            self.screen.addstr(3, 0, 'Current position: {nav}{nav1}'.format(nav=nav.pos, nav1=angles_to_unicode(nav.course)))
            self.screen.addstr(4, 0, 'Current course  : {}'.format(nav.get))
            self.screen.addstr(5, 0, 'Current speed   : {}'.format(nav))
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
        line = 10
        s = self.screen
        s.addstr(line, 0, " " * 30)
        s.nodelay(0)
        curses.echo()
        s.addstr(line, 0, "->")
        command = s.getstr(line, 3)
        curses.noecho()
        s.nodelay(1)
        s.addstr(line, 0, " " * 30)
        return command

    def command(self):
        c = self.get_command()
        if c.strip() == '':
            return

        opt = c.split(' ')

        if opt[0] == 'mov':
            dest = self.parse_coordinates(opt[1])
            if dest:
                self.player_sub.nav.set_destination(dest)
                self.msg("Aye, aye! Destination set to {0}, captain!".format(self.player_sub.nav.destination))
            else:
                self.msg("Invalid input")

        if opt[0] == 'spd':
            if len(opt) == 2:
                n = int(opt[1])
                self.player_sub.nav.speed = n
                self.msg("Changing speed to {0}".format(self.player_sub.nav.destination))


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
                elif k == ord('n') or k == ord('N'):
                    self.display_screen = 'n'
                elif k == ord('r') or k == ord('R'):
                    self.display_screen = 'r'
                elif k == ord('s') or k == ord('S'):
                    self.display_screen = 's'
                elif k == ord('w') or k == ord('W'):
                    self.display_screen = 'w'

            time.sleep(self.update_rate)
            self.update_time()
            self.update_screen()

        # ends and closes interface
        curses.nocbreak()
        s.keypad(0)
        curses.echo(1)
        curses.endwin()





