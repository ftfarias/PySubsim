import curses

def func(win):
    #curses.init_color(0,100,0,0)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_GREEN)
    #curses.nocbreak()
    #win.keypad(0)
    #curses.echo()

    #curses.cbreak(1)
    #for i in  xrange(10):
        #
    for i in  xrange(2):
        win.addstr(i+1,0, 'Testestes')
    win.refresh()
    #win.nodelay(0)
    win.getch()

curses.wrapper(func)


print '\033[95mTestestes'

print '\033[30m'

#print curses.can_change_color()