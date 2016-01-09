# -*- coding: utf-8 -*-
import logging

import scenario
from game_couses_interface import GameCoursesInterface

logger = logging.getLogger("subsim")
logger.setLevel(logging.DEBUG)

# create debug file handler and set level to debug
handler = logging.FileHandler("sub.log", "w")
# handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":
    scenario = scenario.Scenario()
    scenario.initialize()
    scenario.scenary_test_sonar()
    sea = scenario.sea
    player_sub = scenario.player_sub
    interface = GameCoursesInterface(sea, player_sub)
    sea.turn(0.1)
    interface.run()


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

