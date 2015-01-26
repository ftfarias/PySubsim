# -*- coding: utf-8 -*-
import logging

import scenario
from game_text_interface import GameTextInterface

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create debug file handler and set level to debug
handler = logging.FileHandler("sub.log", "w")
# handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":
    scenario = scenario.Scenario()
    scenario.initialize()
    sea = scenario.sea
    player_sub = scenario.player_sub
    interface = GameTextInterface(sea, player_sub)
    sea.turn(0.1)
    interface.run()

