# -*- coding: utf-8 -*-
import logging
import time
import sub688

# import scenario
from game_couses_interface import GameCoursesInterface
# from submarine import sub
# import sea


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

class Gameloop(object):
    def __init__(self):
        pass


    def setup(self):
        self.player_sub = sub688.Submarine688()
        self.interface = GameCoursesInterface(self.player_sub)

        # sea = sea.Sea()
        # # player_sub = scenario.player_sub
        # player_sub = sub.Submarine(sea)
        # interface = GameCoursesInterface(sea, player_sub)
        # scenario = scenario.Scenario()
        # scenario.initialize()
        # scenario.scenary_test_sonar()
        # sea = scenario.sea
        pass


    def update(self, time_elapsed):
        self.player_sub.turn(time_elapsed)  # sea turn runs in hours

    def render(self):
        self.interface.render()

    def run(self):
        self.setup()
        stop = False
        last_time_ref = time.process_time()

        while (not stop):
            try:
                current_time_ref = time.process_time()
                diff_time_ref = current_time_ref - last_time_ref
                last_time_ref = current_time_ref

                time_elapsed = diff_time_ref * time_rate / 3600 # time_elapsed in hours

                # self.getInputs()
                self.interface.read_keyboard()
                # self.player
                self.update(time_elapsed)
                self.render()

            except Exception as e:
                self.interface.finalize()
                print(e)
                logger.exception(e)


if __name__ == "__main__":
    gameloop = Gameloop()
    gameloop.run()


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

