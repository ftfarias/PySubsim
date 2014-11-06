# -*- coding: utf-8 -*-
from sub import ShipFactory
from sea import Sea
from physic import Point
from linear_scale import linear_scaler, linear_scaler2d, AsciiLinearScale, linear_scaler_with_limit
from util import abs_angle_to_bearing, time_length_to_str, angles_to_unicode, shift, ascii_gray, ascii_reset
import time
import sys
import logging
from sonar import Sonar
import math

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


def print_near_objects():
    objs = player_sub.sonar.return_near_objects()
    if not objs:
        print("<no contacts>")
    else:
        for k,v in objs.items():
            print u"{0:3d}: {1}".format(k, v)


def show_object_details(n):
    if n not in player_sub.sonar.contacts:
        print("Unknown track "+str(n))
        print("Valid tracks: ")
        for k,v in player_sub.sonar.contacts.items():
            print(k)
        return
    def f(value, str_format="{0}"):
        if value is None:
            return "?"
        return str_format.format(value)
    obj = player_sub.sonar.contacts[n]
    print (u'{0}'.format(obj))
    print (u"Propeller: blades:{b}  freq: {f}  KPT:{kpt}  est.speed:{s}".format(b=f(obj.blade_number),
                                                                               f=f(obj.blade_frequence),
                                                                               kpt=obj.knots_per_turn,
                                                                               s=f(obj.propeller_speed())))

    n = 10
    start_time = sea.time
    scan_times = []
    for i in xrange(len(obj.time_history[-n:])):
        t = (sea.time - obj.time_history[(-(i+1))])
        scan_times.append(t.seconds)

    times = u" | ".join([u"{0:5s}".format(time_length_to_str(b)) for b in scan_times])
    bearings = u" | ".join([u"{0:5.0f}".format(abs_angle_to_bearing(b)) for b in obj.bearings_history[-n:]])
    ranges = u" | ".join([u"{0:5.1f}".format(b) for b in obj.range_history[-n:]])
    speeds = u" | ".join([u"{0:5.1f}".format(b) for b in obj.speed_history[-n:]])
    courses = u" | ".join([u"{0:5.0f}".format(abs_angle_to_bearing(b)) for b in obj.course_history[-n:]])
    print (u"         {0}".format(times))
    print (u"Bearing: {0}".format(bearings))
    print (u"Range  : {0}".format(ranges))
    print (u"Speed  : {0}".format(speeds))
    print (u"Course : {0}".format(courses))

    bands = obj.bands

    #print("".join(["{0:5}".format(i)  for i in range(1,11)]))
    #print("".join(["{0:5.1f}".format(b) for b in bands]))



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

    pos2map = linear_scaler2d([topleft.x, bottomright.x], [min(x_range), max(x_range)],
                              [topleft.y, bottomright.y], [min(y_range), max(y_range)])

    map2pos_x = linear_scaler([min(x_range), max(x_range)],[topleft.x, bottomright.x])
    map2pos_y = linear_scaler([min(y_range), max(y_range)],[topleft.y, bottomright.y])

    # empty grid
    symbols = [['.']*mc_x_size for x in xrange(mc_y_size)]

    # put symbols in grid
    for k, sc in player_sub.sonar.contacts.items():
        pos = sc.estimate_pos(player_pos)
        if pos is not None:
            x_map, y_map = double_round(pos2map(pos.x, pos.y))
            #s = symbol_for_type(sc.obj_type)
            s = '?'
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
        try:
            #for i, opt in enumerate(menu):
            #    print ("{i} - {opt}".format(i=str(i+1), opt=opt[0]))
            s = ['{0}-{1}'.format(i+1, o[0]) for i,o in enumerate(menu)]
            s = ") (".join(s)
            print("("+s+")")
            option = raw_input('> ')
            if option == '':
                return None
            opt = option.split(" ")

            if opt[0] == '\\':
                n = None
                time_per_turn=0.1
                if len(opt) > 1:
                    n = int(opt[1]/ time_per_turn)
                game_loop(n, time_per_turn=time_per_turn, wait=0.1) # real time
                print_status()
                continue

            if opt[0] == ']':
                n = None
                time_per_turn=0.1
                if len(opt) > 1:
                    n = int(opt[1] / time_per_turn)
                game_loop(n, time_per_turn=0.1, wait=0.01) # 10 times real
                print_status()
                continue

            if opt[0] == '[':
                n = None
                time_per_turn=0.1
                if len(opt) > 1:
                    n = int(opt[1] / time_per_turn)
                game_loop(n, time_per_turn=0.1, wait=0)  # fast as possible, no wait
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
                    show_object_details(n)
                continue


            if opt[0] == 'wf':
                if len(opt) == 2:
                    n = int(opt[1])
                    if n == 1:
                        waterfall.print_waterfall_1m()
                    elif n == 2:
                        waterfall.print_waterfall_30m()
                    else:
                        waterfall.print_waterfall_2h()

                else:
                    waterfall.print_waterfall_1m()

                continue

            if opt[0] == 'spd':
                if len(opt) == 2:
                    n = int(opt[1])
                    player_sub.nav.speed = n
                continue

            if opt[0] == 'deep':
                if len(opt) == 2:
                    n = int(opt[1])
                    player_sub.set_deep = n
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
                print("deep x : set deep to x")
                print("wf <n> : show waterfall display (n=1 for 30 seconds, n=2 for 30 minutes, n=3 for 2 hours")
                print("q      : quit")
        except ValueError as e:  # catchs all other errors inside the big loop
            print e


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


def input_values(msg='(enter coordinates) > '):
    while 1:
        try:
            option = raw_input(msg)
            if option == '':
                return None, None
            if option == '\\':
                return None, None
            coord = option.split(',')
            if len(coord) != 2:
                print('Please enter values as "x,y"')
                continue
            x = int(coord[0])
            y = int(coord[1])
            return x,y
        except ValueError:
            print ('Invalid! Please enter integer values \n')

# Navigation
def move_to():
    x, y = input_values()
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

########## SONAR #############

class Watefall(object):
    def __init__(self):
        self.asciiScaler = None
        self.set_waterfall_level(50,70)

    def set_waterfall_level(self, low, high):
        #self.asciiScaler = AsciiLinearScale([low,high], ascii_scale=".:;|$#").map
        #self.asciiScaler = AsciiLinearScale([low,high], ascii_scale=u"\u2591\u2592\u2593\u2588").map
        self.scaler = linear_scaler_with_limit([low, high], [250, 1])

    def print_sonar(self):
        #s = [self.asciiScaler(x.value) for x in player_sub.sonar.sonar_array(120)]
        line = [ascii_gray(".", int(round(self.scaler(d)))) for d in player_sub.sonar.sonar_array(120)]
        return "[{0}{1}]".format("".join(shift(line, Sonar.WATERFALL_STEPS/2)),ascii_reset())


    def print_waterfall(self, compact=1, l=60, inverted=True):
        """
        Inverted watefall means the most recente events shows in th bottom, not in top
        """
        wf = player_sub.sonar.waterfall[-l:] # filters the last "l" events
        len_wf = len(wf)

        wf_c = []  # compact waterfall
        #print(wf)
        if len_wf == 0:
            print ("no sonar data")
            return

        idx = 0
        while idx < len_wf:
            # idx_compact in the number of sonar readings to be "compacted" for next printed line
            idx_compact = min(compact, len_wf-idx)
            print(idx_compact)
            total = [0.0] * 120
            for _ in xrange(idx_compact):  # compacts the display, calculanting the average
                wf_idx = wf[idx]
                for c in xrange(120):
                    total[c] += wf_idx[c]
                idx += 1

            #print(total)
            #line = [self.asciiScaler(d/idx_compact) for d in total]
            line = [ascii_gray(".", int(round(self.scaler(d/idx_compact)))) for d in total]

            wf_c.append("[{0}{1}]".format("".join(shift(line, Sonar.WATERFALL_STEPS/2)),ascii_reset()))

        if not inverted:
            wf_c.reverse()

        step = 360 / Sonar.WATERFALL_STEPS
        header = [angles_to_unicode(i*step) for i in xrange(Sonar.WATERFALL_STEPS)]
        print(" "+"".join(shift(header,Sonar.WATERFALL_STEPS/2)))

        for l in wf_c:
            print(l)


    def print_waterfall_1m(self):
        self.print_waterfall(compact=1, l=60)

    def print_waterfall_30m(self):
        self.print_waterfall(compact=30, l=1800)

    def print_waterfall_2h(self):
        self.print_waterfall(compact=120, l=7200)

waterfall = Watefall()


def adjust_watefall():
    low, high = input_values("Enter the low and high db levels(default: 50,70): ")
    if low is not None:
        waterfall.set_waterfall_level(low, high)


def print_noise_profile():
    sea_noise = sea.get_background_noise()
    sub_noise = player_sub.self_noise()
    print("Sea background noise: {sea}   Sub noise:{sub}   total:{t}".format(
        sea=sea_noise, sub=sub_noise, t=sea_noise+sub_noise))


MAIN_SONAR = [
    ('Show near objects', print_near_objects),
    ('Waterfall (1 minute)', waterfall.print_waterfall_1m),
    ('Waterfall (30 minutes)', waterfall.print_waterfall_30m),
    ('Waterfall (2 hours)', waterfall.print_waterfall_2h),
    ('Adjust waterfall scale', adjust_watefall),
]


def menu_sonar():
    print(player_sub.sonar.status())
    print_noise_profile()
    print(waterfall.print_sonar())
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
        sea.create_whale()

    # for i in xrange(3):
    #     sea.create_fishing()
    #
    # for i in xrange(2):
    #     sea.create_warship()
    #
    # ship = sea.create_fishing(pos=Point(5,5))
    # ship.set_destination(0, 1)

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
    sea.turn(time_per_turn/3600)  # sea turn runs in hours, run_turn in seconds
    #print(universe)
    sys.stdout.write("\r ({sd}) {nav} deep:{deep:.0f}(set:{sdeep})".format(sd=sea, nav=player_sub.nav,
                                                                       deep=player_sub.actual_deep,
                                                                       sdeep=player_sub.set_deep))
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

