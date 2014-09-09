# -*- coding: utf-8 -*-
from sub import ShipFactory
from sea import Sea,SeaObject
from util import Point
import time
import sys
import math

sea = Sea()
sea.initialize()
player_sub = ShipFactory.create_player_sub(sea)
sea.add_submarine(player_sub)

"""
-2 | -2  -1  0  +1  +2 |
-1 |         D         |
0  |     C       A     |
+1 |         B         |
+2 |                   |

A - 90
B - 180
C - 270
D - 0
"""


def print_near_objects():
    objs = player_sub.sonar.return_near_objects()
    if not objs:
        print("<no contacts>")
    else:
        for i, ob in enumerate(objs):
            print "{0:3o}: {1}".format(i, ob)


def print_status():
    print('* Status *')
    print(player_sub.status())
    print(player_sub.navigation.status())
    print(player_sub.sonar.status())
    print(player_sub.weapons.status())


def menu_object(n):
    obj = player_sub.sensors.return_near_objects()[n]
    print (obj)
    bands = obj.bands
    print("".join(["{0:5}".format(i)  for i in range(1,11)]))
    print("".join(["{0:5.1f}".format(b) for b in bands]))
    for prob in obj.obj_type_probs:
        print("Ref:{0:20}  Prob:{1:3.3f}".format(prob[1], prob[0]))


def parse_coordinates(text):
    try:
        coord = text.split(',')
        if len(coord) != 2:
            return None
        x = float(coord[0])
        y = float(coord[1])
        return Point(x,y)
    except ValueError:
        return None

def print_map():
    x_size = 12
    y_size = 12
    player_pos = player_sub.get_pos()
    topleft = player_pos - Point(x_size/2, -y_size/2)
    bottomright = player_pos + Point(x_size/2, -y_size/2)
    print(topleft)
    print(bottomright)

    y_range = range(int(topleft.y),int(bottomright.y),-1)
    x_range = range(int(topleft.x), int(bottomright.x))
    grid = []
    for y in y_range:
        line = []
        #print(y)
        for x in x_range:
            xy = Point(x,y)
            dist = player_pos.distance_to(xy)
            #line.append(str(int(dist)))
            for obj in player_sub.sonar.objects:
                if round(obj.pos.x) == round(xy.x) and \
                   round(obj.pos.y) == round(xy.y):
                    if obj.obj_type is None:
                        s = '?'
                    else:
                        s = obj.obj_type[0]
                    break
                else:
                    if dist <= 5.5:
                        s = '.'
                    else:
                        s = ' '
            line.append(s)
        grid.append(line)

    #line = "." * x_size
    #grid = [line for _ in xrange(y_size)]

    #
    # print ("     +"+("-"*(x_size*2-1))+"+")
    print ("     "+"".join(["{0:+3}".format(x) for x in x_range]))
    for i, y in enumerate(y_range):
        print ("{idx:5}|{linha}|".format(idx=y, linha="  ".join(grid[i])))



def show_menu(menu):
    while 1:
        #for i, opt in enumerate(menu):
        #    print ("{i} - {opt}".format(i=str(i+1), opt=opt[0]))
        s = ['{0}-{1}'.format(i+1, o[0]) for i,o in enumerate(menu)]
        s = ") (".join(s)
        print("("+s+")")
        option = raw_input('> ')
        if option == '':
            return None
        opt = option.split(" ")

        if opt[0] == ']':  # 1 second
            n = 10
            if len(opt) > 1:
                n = int(opt[1])
            game_loop(n, wait=0.1)
            print_status()
            continue

        if opt[0] == '[': # 1 minute
            n = 60 * 10
            if len(opt) > 1:
                n = int(opt[1])
            game_loop(n, wait=0.01)
            print_status()
            continue

        if opt[0] == 's':
            print_status()
            continue

        if opt[0] == 'o':
            if len(opt) == 1:
                print_near_objects()
            else:
                n = int(opt[1])
                menu_object(n)
            continue

        if opt[0] == 'mov':
            dest = parse_coordinates(opt[1])
            if dest:
                player_sub.set_destination(dest)
                print("Destination set to {0}".format(player_sub.navigation.destination))
            else:
                print("Invalid input")
            continue

        if opt[0] == 'm':
            print_map()
            continue

        try:
            int_opt = int(option)
            if 1 <= int_opt <= len(menu):
                return menu[int_opt-1][1]
            raise ValueError()
        except ValueError:
            print("Please choose a valid option:")
            print("<number>: choose a option")
            print("<empty>: return to previous menu")
            print("]: run game for 1 second")
            print("] <n>: run game for n seconds")
            print("[: run game for 1 minute")
            print("[ <n>: run game for n minutes\n")


def input_integer(min=0, max=100):
    while 1:
        try:
            option = raw_input('(enter integer [{0},{1}]) > '.format(min,max))
            if option == '':
                return None
            x = int(option)
            return x
        except ValueError:
            print ("Invalid entry! \n")


def input_coordinates():
    while 1:
        try:
            option = raw_input('(enter coordinates) > ')
            if option == '\\':
                return None, None
            coord = option.split(',')
            if len(coord) != 2:
                print('Please enter as "x,y"')
                continue
            x = int(coord[0])
            y = int(coord[1])
            return x,y
        except ValueError:
            print ("Invalid Coordinates! \n")

# Navigation
def move_to():
    x, y = input_coordinates()
    if x is None or y is None:
        return
    player_sub.set_destination(Point(x, y))


def set_speed():
    new_speed = input_integer()
    if new_speed:
        player_sub.set_speed(new_speed)

MAIN_NAVIGATION = [
    ('Move to', move_to),
    ('Stop', player_sub.stop_moving),
    ('Set speed', set_speed)
   # ('Land', None),
   # ('Take Off', None),
]

def menu_navigation():
    print("* Navigation *")
    print(player_sub.navigation.status())
    opt = show_menu(MAIN_NAVIGATION)
    if opt:
        opt()
    main()

# Sensors
MAIN_SENSORS = [
    ('Show near objects', print_near_objects),
   # ('Land', None),
   # ('Take Off', None),
]


def menu_sonar():
    print(player_sub.sonar.status())
    opt = show_menu(MAIN_SENSORS)
    if opt:
        opt()
    main()

# TMA

MAIN_TMA = [
    ('', None),
    ('', None),
   # ('Land', None),
   # ('Take Off', None),
]

def menu_tma():
    print("Target Motion Analysis")
    print(player_sub.tma.status())
    opt = show_menu(MAIN_TARGET)
    if opt:
        opt()
    main()


# Weapons

MAIN_TARGET = [
    ('Set Target', None),
    ('Fire', None),
   # ('Land', None),
   # ('Take Off', None),
]

def menu_weapons():
    print("Weapons")
    print(player_sub.target.status())
    opt = show_menu(MAIN_TARGET)
    if opt:
        opt()
    main()


# communications

MAIN_COMM = [
    ('', None),
    ('', None),
   # ('Take Off', None),
]

def menu_comm():
    opt = show_menu(MAIN_COMM)
    if opt:
        opt()
    main()

# Main

MAIN_MENU = [
    ('Navigation', menu_navigation),
    ('Sonar', menu_sonar),
    ('TMA', menu_tma),
    ('Weapons', menu_weapons),
    ('Communication', menu_comm),
]


def start():
    #dummy_ship = ShipFactory.create_simple_sub(sea, Point(30, 30))
    #sea.create_smallboat(dummy_ship)

    """
    dummy_ship = ShipFactory.create_simple_ship(universe, Point(0, 1))
    universe.add_ship(dummy_ship)
    dummy_ship = ShipFactory.create_simple_ship(universe, Point(-1, 0))
    universe.add_ship(dummy_ship)
    dummy_ship = ShipFactory.create_simple_ship(universe, Point(0, -1))
    universe.add_ship(dummy_ship)
    dummy_ship = ShipFactory.create_simple_ship(universe, Point(1, 1))
    universe.add_ship(dummy_ship)
    dummy_ship = ShipFactory.create_simple_ship(universe, Point(2, 8))
    universe.add_ship(dummy_ship)
    """
    for i in xrange(5):
        sea.create_biologic()

    for i in xrange(5):
        sea.create_smallboat()

    game_loop(1, 0.1)


def game_loop(turns, time_per_turn=0.1, wait=0.01):
    for i in xrange(turns):
        sea.turn(time_per_turn)
        #print(universe)
        sys.stdout.write("\rPos:{pos:10} ({sd}) ".format(pos=player_sub.get_pos(), sd=sea))
        sys.stdout.flush()
        time.sleep(wait)
        messages, stop = player_sub.get_messages()
        if messages:
            print("\n@{0}".format(sea.time))
            for m in messages:
                print("\t{0}".format(m))
            time.sleep(1)
            player_sub.clear_messages()
            if stop:
                break


def main():
    while 1:
        print("Main (Time: {0})".format(sea.time))
        messages, stop = player_sub.get_messages()
        if messages:
            for m in messages:
                print("\t{0}".format(m))
        opt = show_menu(MAIN_MENU)
        if opt:
            opt()

if __name__ == "__main__":
    start()
    main()

