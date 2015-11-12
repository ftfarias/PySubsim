# -*- coding: utf-8 -*-
import time
import sys

from util.physic import Point
from linear_scale import linear_scaler, linear_scaler2d
from util import abs_angle_to_bearing, time_length_to_str, int_to_hertz
from game_waterfall import Waterfall
import sound


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


class GameTextInterface(object):
    def __init__(self, sea, player_sub):
        self.player_sub = player_sub
        self.sea = sea
        self.selected_object_detail = None
        self.waterfall = Waterfall(player_sub.sonar)

    def print_status(self):
        print('* Status *')
        print(self.player_sub.nav.status())
        print(self.player_sub.sonar.status())
        print(self.player_sub)
        # print(player_sub.weapons.status())


    def get_text(self, text='> '):
        option = raw_input(text)
        return option


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


    def print_near_objects(self):
        objs = self.player_sub.sonar.return_near_objects()
        if not objs:
            print("<no contacts>")
        else:
            for i,obj in enumerate(objs):
                print u"{0:3d}: {1}".format(i, obj)


    def obj_change_name(self):
        new_name = self.get_text("Name for contact {0}: ".format(selected_object_detail.ident))
        selected_object_detail.name = new_name


    OBJECT_DETAIL_MENU = [
        (u'Change name ', obj_change_name),
        (u'Send to TMA ', None),

        # ('Land', None),
        # ('Take Off', None),
    ]


    def show_object_details(self, n):
        if n not in self.player_sub.sonar.contacts:
            print("Unknown track " + str(n))
            print("Valid tracks: ")
            for k, v in self.player_sub.sonar.contacts.items():
                print(k)
            return

        def f(value, str_format=u"{0}"):
            if value is None:
                return "?"
            return str_format.format(value)

        obj = self.player_sub.sonar.contacts[n]
        print (u'{0}'.format(obj))
        print (u"Propeller: blades:{b}  freq: {f}  KPT:{kpt}  est.speed:{s}".format(b=f(obj.blade_number),
                                                                                    f=f(obj.blade_frequence),
                                                                                    kpt=obj.knots_per_turn,
                                                                                    s=f(obj.propeller_speed())))

        n = 10
        start_time = self.sea.time
        scan_times = []
        for i in xrange(len(obj.time_history[-n:])):
            t = (self.sea.time - obj.time_history[(-(i + 1))])
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
        print bands

        # print("".join(["{0:5}".format(i)  for i in range(1,11)]))
        # print("".join(["{0:5.1f}".format(b) for b in bands]))

        # for prob in obj.obj_type_probs:
        #    print("Ref:{0:20}  Prob:{1:3.3f}".format(prob[1], prob[0]))
        global selected_object_detail
        selected_object_detail = obj
        opt = self.show_menu(self.OBJECT_DETAIL_MENU)
        if opt:
            opt()


    def print_map(self):
        h = ["P - Player Sub",
             "^ - Warship",
             "M - Merchant Ship",
             ""]

        def double_round(x):
            return int(round(x[0])), int(round(x[1]))

        # all variables with (M)ap (C)oordinates begins with "mc_"
        # all variables with (G)ame (C)oordinates begins with "gc_"
        mc_x_size = 12  # from 0 to 11
        mc_y_size = 12  # from 0 to 11
        x_range = range(mc_x_size)
        y_range = range(mc_y_size)

        player_pos = self.player_sub.get_pos()
        topleft = player_pos - Point(mc_x_size / 2, mc_y_size / 2)
        bottomright = player_pos + Point(mc_x_size / 2 - 1, mc_y_size / 2 - 1)

        pos2map = linear_scaler2d([topleft.x, bottomright.x], [min(x_range), max(x_range)],
                                  [topleft.y, bottomright.y], [min(y_range), max(y_range)])

        map2pos_x = linear_scaler([min(x_range), max(x_range)], [topleft.x, bottomright.x])
        map2pos_y = linear_scaler([min(y_range), max(y_range)], [topleft.y, bottomright.y])

        # empty grid
        symbols = [['.'] * mc_x_size for x in xrange(mc_y_size)]

        # put symbols in grid
        for k, sc in self.player_sub.sonar.contacts.items():
            pos = sc.estimate_pos(player_pos)
            if pos is not None:
                x_map, y_map = double_round(pos2map(pos.x, pos.y))
                # s = symbol_for_type(sc.obj_type)
                s = '?'
                if 0 <= x_map < mc_x_size and 0 <= y_map < mc_y_size:
                    symbols[x_map][y_map] = s

        # player pos:
        x_map, y_map = double_round(pos2map(player_pos.x, player_pos.y))
        symbols[x_map][y_map] = "P"

        # y_range = range(int(topleft.y),int(bottomright.y),-1)
        # x_range = range(int(topleft.x), int(bottomright.x))

        # line = "." * x_size
        #grid = [line for _ in xrange(y_size)]

        #
        # print ("     +"+("-"*(x_size*2-1))+"+")
        print ("     " + "".join(["{0:+3}".format(int(round(map2pos_x(x)))) for x in x_range]))
        for i, y in enumerate(y_range):
            print ("{idx:5}|{linha}|".format(idx=int(round(map2pos_y(y))), linha="  ".join(symbols[i])))


    def debug(self):
        self.sea.debug()


    def show_menu(self, menu):
        while 1:
            try:
                # for i, opt in enumerate(menu):
                # print ("{i} - {opt}".format(i=str(i+1), opt=opt[0]))
                s = ['{0}-{1}'.format(i + 1, o[0]) for i, o in enumerate(menu)]
                s = ") (".join(s)
                print("(" + s + ")")
                option = raw_input('> ')
                if option == '':
                    return None
                opt = option.split(" ")

                time_per_turn = 0.1
                if opt[0] == '\\':
                    n = None
                    if len(opt) > 1:
                        n = int(opt[1] / time_per_turn)
                    self.game_loop(n, time_per_turn=time_per_turn, wait=0.1)  # real time
                    self.print_status()
                    continue

                if opt[0] == ']':
                    n = None
                    if len(opt) > 1:
                        n = int(opt[1] / time_per_turn)
                    self.game_loop(n, time_per_turn=time_per_turn, wait=0.01)  # 10 times real
                    self.print_status()
                    continue

                if opt[0] == '[':
                    n = None
                    if len(opt) > 1:
                        n = int(opt[1] / time_per_turn)
                    self.game_loop(n, time_per_turn=time_per_turn, wait=0)  # fast as possible, no wait
                    self.print_status()
                    continue

                if opt[0] == 's':
                    self.print_status()
                    continue

                if opt[0] == 'o':
                    if len(opt) == 1:
                        self.print_near_objects()
                    else:
                        n = int(opt[1])
                        self.show_object_details(n)
                    continue

                if opt[0] == 'debug':
                    self.debug()
                    continue

                if opt[0] == 'wf':
                    if len(opt) == 2:
                        n = int(opt[1])
                        if n == 1:
                            self.waterfall.print_waterfall_1m()
                        elif n == 2:
                            self.waterfall.print_waterfall_30m()
                        else:
                            self.waterfall.print_waterfall_2h()

                    else:
                        self.waterfall.print_waterfall_1m()

                    continue

                if opt[0] == 'spd':
                    if len(opt) == 2:
                        n = int(opt[1])
                        self.player_sub.nav.speed = n
                    continue

                if opt[0] == 'deep':
                    if len(opt) == 2:
                        n = int(opt[1])
                        self.player_sub.set_deep = n
                    continue

                if opt[0] == 'mov':
                    dest = self.parse_coordinates(opt[1])
                    if dest:
                        self.player_sub.nav.set_destination(dest)
                        print("Destination set to {0}".format(self.player_sub.nav.destination))
                    else:
                        print("Invalid input")
                    continue

                if opt[0] == 'm':
                    self.print_map()
                    continue

                if opt[0] == 'q':
                    sys.exit(0)
                    continue

                try:
                    int_opt = int(option)
                    if 1 <= int_opt <= len(menu):
                        return menu[int_opt - 1][1]
                    raise ValueError()
                except ValueError:
                    print("Please choose a valid option:")
                    print("<number>: choose a option")
                    print("<empty>: return to previous menu")
                    print("\      : run game in real time")
                    print("] <n>  : run game in real time for n seconds")
                    print("]      : run game 10 times faster")
                    print("] <n>  : run game 10 times faster for n seconds")
                    print("[      : run game fast as possible")
                    print("[ <n>  : run game fast as possible for n seconds")
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


    def input_integer(self, min=0, max=100):
        while 1:
            try:
                option = raw_input('(enter integer [{0},{1}]) > '.format(min, max))
                if option == '':
                    return None
                x = int(option)
                return x
            except ValueError:
                print ("Invalid entry! \n")


    def input_values(self, msg='(enter coordinates) > '):
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
                return x, y
            except ValueError:
                print ('Invalid! Please enter integer values \n')


    # Navigation
    def move_to(self):
        x, y = self.input_values()
        if x is None or y is None:
            return
        self.player_sub.set_destination(Point(x, y))
        print("Aye, sir! {0}".format(self.player_sub.nav.status()))


    def set_speed(self):
        new_speed = self.input_integer(0, 30)
        if new_speed:
            self.player_sub.set_speed(new_speed)


    def menu_navigation(self):
        MAIN_NAVIGATION = [
            ('Move to (MOV x,y)', self.move_to),
            ('Stop', self.player_sub.stop_moving),
            ('Set speed (SPD s)', self.set_speed),
            ('Rudder left', self.player_sub.rudder_left),
            ('Rudder center', self.player_sub.rudder_center),
            ('Rudder right', self.player_sub.rudder_right)

            # ('Land', None),
            # ('Take Off', None),
        ]
        print("* Navigation *")
        print(self.player_sub.nav.status())
        opt = self.show_menu(MAIN_NAVIGATION)
        if opt:
            opt()


    ########## SONAR #############
    def adjust_watefall(self):
        low, high = self.input_values("Enter the low and high db levels(default: 50,70): ")
        if low is not None:
            self.waterfall.set_waterfall_level(low, high)


    def print_noise_profile(self):
        sea_noise = self.sea.get_background_noise()
        sub_noise = self.player_sub.self_noise(50)
        print("Sea background noise: {sea:5.1f}   Sub noise:{sub:5.1f}   total:{t:5.1}".format(
            sea=sea_noise, sub=sub_noise, t=sea_noise + sub_noise))


    def sea_conditions(self):
        print("Sea Conditions:")
        print("\tSea conditions: {sea}".format(sea=self.sea.conditions))
        print("\tSea noise: {sea}".format(sea=self.sea.get_background_noise()))
        print("\tSea temperature: {sea} Celsius".format(sea=self.sea.temperature))
        print("\tSea salinity: {sea} ppt".format(sea=self.sea.salinity))
        print("\tSea Acidity: pH {sea}".format(sea=self.sea.ph))
        print("Sea sound absortion (50 meters deep):")
        for v in sound.REFERENCE_FREQS:
            print("\t{0}: {1}".format(int_to_hertz(v), self.sea.sound_absortion_by_sea(v, 50,
                                                                                       temperature=self.sea.temperature,
                                                                                       salinity=self.sea.salinity,
                                                                                       pH=self.sea.ph
            )))


    def menu_waterfall(self):
        WATERFALL = [
            ('Waterfall (1 minute)', self.waterfall.print_waterfall_1m),
            ('Waterfall (30 minutes)', self.waterfall.print_waterfall_30m),
            ('Waterfall (2 hours)', self.waterfall.print_waterfall_2h),
            ('Adjust waterfall scale', self.adjust_watefall),
        ]
        print(self.player_sub.sonar.status())
        self.print_noise_profile()
        print(self.waterfall.print_sonar())
        opt = self.show_menu(WATERFALL)
        if opt:
            opt()


    def deploy_towed(self):
        self.player_sub.sonar.deploy_towed_array()
        print (self.player_sub.sonar.towed)

    def retrieve_towed(self):
        self.player_sub.sonar.retrieve_towed_array()
        print (self.player_sub.sonar.towed)

    def stop_towed(self):
        self.player_sub.sonar.stop_towed_array()
        print (self.player_sub.sonar.towed)


    def menu_sonar(self):
        MAIN_SONAR = [
            ('Show near objects', self.print_near_objects),
            ('Waterfall', self.menu_waterfall),
            ('Sea conditions', self.sea_conditions),
            ('Deploy Towed Array', self.deploy_towed),
            ('Retreive Towed Array', self.retrieve_towed),
            ('Stop Towed Array', self.stop_towed),

        ]
        print(self.player_sub.sonar.status())
        self.print_noise_profile()
        print(self.waterfall.print_sonar())
        opt = self.show_menu(MAIN_SONAR)
        if opt:
            opt()

    # TMA
    def menu_tma(self):
        MAIN_TMA = [
            ('', None),
            ('', None),
            # ('Land', None),
            # ('Take Off', None),
        ]
        print("Target Motion Analysis")
        print(self.player_sub.tma.status())
        opt = self.show_menu(MAIN_TMA)
        if opt:
            opt()


    # Weapons
    def menu_weapons(self):
        MAIN_TARGET = [
            ('Set Target', None),
            ('Fire', None),
            # ('Land', None),
            # ('Take Off', None),
        ]
        print("Weapons")
        print(self.player_sub.target.status())
        opt = self.show_menu(MAIN_TARGET)
        if opt:
            opt()


    def menu_comm(self):
        # communications
        MAIN_COMM = [
            ('', None),
            ('', None),
            # ('Take Off', None),
        ]
        opt = self.show_menu(MAIN_COMM)
        if opt:
            opt()

    # Main

    MAIN_MENU = [
        ('Navigation', menu_navigation),
        ('Sonar', menu_sonar),
        ('TMA', menu_tma),
        ('Weapons', menu_weapons),
        ('Communication', menu_comm),
    ]

    def game_loop(self, turns, time_per_turn=0.1, wait=0.01):
        try:
            if turns is None:
                while 1:
                    self.run_turn(time_per_turn)
                    time.sleep(wait)
            else:
                for i in xrange(turns):
                    time.sleep(wait)
                    self.run_turn(time_per_turn)
        except KeyboardInterrupt:
            pass


    def run_turn(self, time_per_turn):
        # print(universe)
        sys.stdout.write("\r ({sd}) {nav} deep:{deep:.0f}(set:{sdeep})".format(sd=self.sea, nav=self.player_sub.nav,
                                                                               deep=self.player_sub.actual_deep,
                                                                               sdeep=self.player_sub.set_deep))
        sys.stdout.flush()
        messages, stop = self.player_sub.get_messages()
        if messages:
            print("\n@{0}".format(self.sea.time))
            for m in messages:
                print("\t{0}".format(m))
            time.sleep(1)
            self.player_sub.clear_messages()


    def run(self):
        while 1:
            try:
                print("Main (Time: {0})".format(self.sea.time))
                messages, stop = self.player_sub.get_messages()
                if messages:
                    for m in messages:
                        print("\t{0}".format(m))
                opt = self.show_menu(self.MAIN_MENU)
                if opt:
                    opt(self)
            except KeyboardInterrupt:
                pass


