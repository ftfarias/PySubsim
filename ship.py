# -*- coding: utf-8 -*-
import unittest

from util.point import Point
from util.util import limits
from util.physic import MovableNewtonObject


class Ship(MovableNewtonObject):
    def __init__(self, max_turn_per_hour):
        super(Ship, self).__init__()
        self._rudder = 0
        self.max_turn_per_hour = max_turn_per_hour

    def get_rudder(self):
        return self._rudder

    def set_rudder(self, angle):
        angle = limits(angle, -self.max_turn_per_hour, self.max_turn_per_hour)
        self._rudder = angle

    rudder = property(get_rudder, set_rudder, "Rudder")

    def rudder_right(self):
        self.rudder = self.max_turn_per_hour

    def rudder_left(self):
        self.rudder = -self.max_turn_per_hour

    def rudder_center(self):
        self.rudder = 0

    def turn(self, time_elapsed):  # time in seconds
        if self.rudder != 0:
            self.rotate(self.rudder * time_elapsed)
        super(Ship, self).turn(time_elapsed)


    def __str__(self):
        return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚) rudder:{rudder}".format(
            p=self._position,
            v=self._velocity,
            vt=self._velocity.angle,
            va=self._velocity.bearing,
            a=self._acceleration,
            at=self._acceleration.angle,
            aa=self._acceleration.bearing,
            rudder=self.rudder)

    def debug(self):
        return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚)".format(
            p=self._position,
            v=self._velocity,
            vt=self._velocity.angle,
            va=self._velocity.bearing,
            a=self._acceleration,
            at=self._acceleration.angle,
            aa=self._acceleration.bearing)

class TestUtil(unittest.TestCase):

    def test_mov_stopped(self):
        m1 = Ship()
        m1.turn(20)
        self.assertEqual(m1.position, Point(0, 0))


if __name__ == '__main__':
    unittest.main()