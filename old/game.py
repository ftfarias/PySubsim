# -*- coding: utf-8 -*-
import logging

import scenario
from game_couses_interface import GameCoursesInterface
from submarine import sub
import sea
import time


logger = logging.getLogger("subsim")
logger.setLevel(logging.DEBUG)

# create debug file handler and set level to debug
handler = logging.FileHandler("sub.log", "w")
# handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

time_rate = 1  # 1 time(s) faster
update_rate = 0.1  # updates every 0.1 second

if __name__ == "__main__":
    # scenario = scenario.Scenario()
    # scenario.initialize()
    # scenario.scenary_test_sonar()
    # sea = scenario.sea


    sea = sea.Sea()
    # player_sub = scenario.player_sub
    player_sub = sub.Submarine(sea)
    interface = GameCoursesInterface(sea, player_sub)

    try:
        while True:
            time_elapsed = time_rate * update_rate / 3600 # time_elapsed in hours
            sea.turn(time_elapsed)  # sea turn runs in hours
            player_sub.turn(time_elapsed)  # sea turn runs in hours
            interface.update_screen()
            time.sleep(update_rate)
    except Exception as e:
        print(e)
        interface.finalize()


# def init_colors(s):
#     curses.start_color()
#     curses.use_default_colors()
#     cpt = 0
#     for i in range(-1, 8):
#         for y in range(-1, 8):
#             curses.init_pair(cpt, y, i)
#             # display the just-initialized color onscreen
#             s.addstr(str(cpt), curses.color_pair(cpt))
#             s.addstr(' ')
#             s.refresh()
#             cpt += 1

# if __name__ == '__main__':
#     main()

