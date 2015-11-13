# -*- coding: utf-8 -*-
import math

from sub_module import SubModule
from util.util import limits

tma_sources = {
    "sonar":{ "name":"Sonar" },
    "radar":{ "name":"Radar" }
}

class Turbine(SubModule):
    def __init__(self, ship,  max_acceleration):
        '''
        :param max_acceleration: maximum acceleration in knots / second
        :return:
        '''
        self.max_acceleration = max_acceleration
        self._level = 0  # 0 to 100%
        self.ship = ship

    def get_level(self):
        return self._level

    def _set_level(self, new_level):
        self._level = limits(new_level, -100, 100)

    level = property(get_level, _set_level, None, "level of power in the turbine (0-100%)")

    def get_acceleration(self):
        return self.max_acceleration * self._level / 100.0

