# -*- coding: utf-8 -*-
from sub import ShipFactory
from sea import Sea, symbol_for_type
from physic import Point
from linear_scale import linear_scaler,linear_scaler2d
import time
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create debug file handler and set level to debug
handler = logging.FileHandler("sub.log","w")
#handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

sea = Sea()
sea.initialize()
player_sub = ShipFactory.create_player_sub(sea)

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




def print_status():
    print('* Status *')
    #print(player_sub.status())
    print(player_sub.nav.status())
    print(player_sub.sonar.status())
    print(player_sub)
    #print(player_sub.weapons.status())


def menu_object(n):
    def f(value, str_format="{0}"):
        if value is None:
            return "?"
        return str_format.format(value)
    obj = player_sub.sonar.contacts[n]
    print (obj)
    print ("Propeller: blades:{b}  freq: {f}  KPT:{kpt}  est.speed:{s}".format(b=f(obj.blade_number), f=f(obj.blade_frequence),
        kpt=obj.knots_per_turn, s=f(obj.propeller_speed())))
    bands = obj.bands
    print("".join(["{0:5}".format(i)  for i in range(1,11)]))
    print("".join(["{0:5.1f}".format(b) for b in bands]))
    #for prob in obj.obj_type_probs:
    #    print("Ref:{0:20}  Prob:{1:3.3f}".format(prob[1], prob[0]))


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
    h = ["P - Player Sub",
         "^ - Warship",
         "M - Merchant Ship",
         ""]

    def double_round(x):
        return int(round(x[0])),int(round(x[1]))
    # all variables with map coordinates begins with "mc_"
    # all variables with game coordinates begins with "gc_"
    mc_x_size = 12  # from 0 to 11
    mc_y_size = 12  # from 0 to 11
    x_range = range(mc_x_size)
    y_range = range(mc_y_size)

    player_pos = player_sub.get_pos()
    topleft = player_pos - Point(mc_x_size/2, mc_y_size/2)
    bottomright = player_pos + Point(mc_x_size/2 - 1, mc_y_size/2 - 1)
    print(x_range)
    print(y_range)
    print(topleft)
    print(bottomright)

    pos2map = linear_scaler2d([topleft.x, bottomright.x], [min(x_range), max(x_range)],
                              [topleft.y, bottomright.y], [min(y_range), max(y_range)])

    map2pos_x = linear_scaler([min(x_range), max(x_range)],[topleft.x, bottomright.x])
    map2pos_y = linear_scaler([min(y_range), max(y_range)],[topleft.y, bottomright.y])

    print(pos2map(4,5))

    # empty grid
    symbols = [['.']*mc_x_size for x in xrange(mc_y_size)]

    # put symbols in grid
    for k, sc in player_sub.sonar.contacts.items():
        pos = sc.estimate_pos(player_pos)
        if pos is not None:
            x_map, y_map = double_round(pos2map(pos.x, pos.y))
            s = symbol_for_type(sc.obj_type)
            if 0 <=x_map<mc_x_size and 0<=y_map<mc_y_size:
                symbols[x_map][y_map] = s

    # player pos:
    x_map, y_map = double_round(pos2map(player_pos.x, player_pos.y))
    symbols[x_map][y_map] = "P"

    #y_range = range(int(topleft.y),int(bottomright.y),-1)
    #x_range = range(int(topleft.x), int(bottomright.x))

    #line = "." * x_size
    #grid = [line for _ in xrange(y_size)]

    #
    # print ("     +"+("-"*(x_size*2-1))+"+")
    print ("     "+"".join(["{0:+3}".format(int(round(map2pos_x(x)))) for x in x_range]))
    for i, y in enumerate(y_range):
        print ("{idx:5}|{linha}|".format(idx=int(round(map2pos_y(y))), linha="  ".join(symbols[i])))


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

        if opt[0] == ']':
            n = None
            time_per_turn=0.1
            if len(opt) > 1:
                n = int(opt[1]/ time_per_turn)
            game_loop(n, time_per_turn=time_per_turn, wait=0.1) # real time
            print_status()
            continue

        if opt[0] == '[':
            n = None
            time_per_turn=0.1
            if len(opt) > 1:
                n = int(opt[1] / time_per_turn)
            game_loop(n, time_per_turn=0.1, wait=0.01) # 10 times real
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

        if opt[0] == 'spd':
            if len(opt) == 2:
                n = int(opt[1])
                player_sub.nav.speed = n
            continue

        if opt[0] == 'mov':
            dest = parse_coordinates(opt[1])
            if dest:
                player_sub.nav.set_destination(dest)
                print("Destination set to {0}".format(player_sub.nav.destination))
            else:
                print("Invalid input")
            continue

        if opt[0] == 'm':
            print_map()
            continue

        if opt[0] == 'q':
            sys.exit(0)
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
            print("]      : run game in real time")
            print("] <n>  : run game in real time for n seconds")
            print("[      : run game 10 times faster")
            print("[ <n>  : run game 10 times faster for n seconds")
            print("s      : Show status")
            print("o      : Show objects in sonar")
            print("o <n>  : Show detail information about object")
            print("m      : Show map")
            print("mov x,y: set destination x,y")
            print("spd x  : set speed for x")
            print("q      : quit")


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
    print("Aye, sir! {0}".format(player_sub.nav.status()))


def set_speed():
    new_speed = input_integer(0, 30)
    if new_speed:
        player_sub.set_speed(new_speed)

MAIN_NAVIGATION = [
    ('Move to (MOV x,y)', move_to),
    ('Stop', player_sub.stop_moving),
    ('Set speed (SPD s)', set_speed),
    ('Rudder left', player_sub.rudder_left),
    ('Rudder center', player_sub.rudder_center),
    ('Rudder right', player_sub.rudder_right)

   # ('Land', None),
   # ('Take Off', None),
]

def menu_navigation():
    print("* Navigation *")
    print(player_sub.nav.status())
    opt = show_menu(MAIN_NAVIGATION)
    if opt:
        opt()
    main()



def print_near_objects():
    objs = player_sub.sonar.return_near_objects()
    if not objs:
        print("<no contacts>")
    else:
        for k,v in objs.items():
            print "{0:3o}: {1}".format(k, v)

def print_noise_profile():
    sea_noise = sea.get_background_noise()
    sub_noise = player_sub.self_noise()
    print("Sea background noise: {sea}   Sub noise:{sub}".format(sea=sea_noise, sub=sub_noise))


# Sensors
MAIN_SONAR = [
    ('Show near objects', print_near_objects),
   # ('Land', None),
    ('Noise Profile', print_noise_profile),
]


def menu_sonar():
    print(player_sub.sonar.status())
    opt = show_menu(MAIN_SONAR)
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
    for i in xrange(2):
        sea.create_biologic()

    for i in xrange(3):
        sea.create_fishing()

    for i in xrange(2):
        sea.create_warship()

    game_loop(1, 0.1)


def game_loop(turns, time_per_turn=0.1, wait=0.01):
    try:
        if turns is None:
            while 1:
                run_turn(time_per_turn)
                time.sleep(wait)
        else:
            for i in xrange(turns):
                time.sleep(wait)
                run_turn(time_per_turn)
    except KeyboardInterrupt:
        pass


def run_turn(time_per_turn):
    sea.turn(time_per_turn)
    #print(universe)
    sys.stdout.write("\r ({sd}) {nav} ".format(sd=sea, nav=player_sub.nav))
    sys.stdout.flush()
    messages, stop = player_sub.get_messages()
    if messages:
        print("\n@{0}".format(sea.time))
        for m in messages:
            print("\t{0}".format(m))
        time.sleep(1)
        player_sub.clear_messages()


def main():
    while 1:
        try:
            print("Main (Time: {0})".format(sea.time))
            messages, stop = player_sub.get_messages()
            if messages:
                for m in messages:
                    print("\t{0}".format(m))
            opt = show_menu(MAIN_MENU)
            if opt:
                opt()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    start()
    main()

