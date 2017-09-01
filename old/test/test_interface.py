# -*- coding: utf-8 -*-
import curses
import threading
import time
import locale
# def init_colors(s):
#
#     cpt = 0
#     for i in range(-1, 8):
#         for y in range(-1, 8):
#             curses.init_pair(cpt, y, i)
#             # display the just-initialized color onscreen
#             s.addstr(str(cpt), curses.color_pair(cpt))
#             s.addstr(' ')
#             s.refresh()
#             cpt += 1
#
# def timer():
#
#     threading.Timer()
#
# def main(s):
#     s.getch()
#     curses.endwin()
 
# if __name__ == '__main__':
#     main()

myscreen = curses.initscr()
myscreen.nodelay(1)
curses.noecho()
curses.start_color()
curses.use_default_colors()
# curses.curs_set(0)
# myscreen.keypad(1)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
strcode = locale.getpreferredencoding()
print(strcode)


myscreen.border(0)
myscreen.addstr(12, 25, "Python curses in action!")
myscreen.addstr(13, 20, u'\u2219'.encode("UTF8"))
myscreen.addstr(0, 0, "!")
myscreen.refresh()
while 1:
    a = myscreen.getch()
    if a != curses.ERR:
        # curses.flash()
        myscreen.addstr(0,1,str(a))
        myscreen.refresh()
        if a == ord('q'):
            break
    time.sleep(1.0)
    myscreen.addstr(1, 30, str(time.time()))
    myscreen.refresh()

curses.echo()
curses.endwin()