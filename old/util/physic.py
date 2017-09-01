# -*- coding: utf-8 -*-

from point import Point
from util import normalize_angle_2pi


class MovableNewtonObject(object):
    def __init__(self):
        self._position = Point(0, 0)
        self._velocity = Point(0, 0)
        self._acceleration = Point(0, 0)

    def get_speed(self):
        return self._velocity.length

    def _set_speed(self, value):
        self._velocity.length = value

    speed = property(get_speed, _set_speed, None, "Speed")

    def get_position(self):
        return self._position

    def _set_position(self, value):
        self._position = value

    position = property(get_position, _set_position, None, "Position")




    # def set_speed(self, new_speed):
    #     self.nav.speed = new_speed

    # Destination

    # def set_destination(self, destination):
    #     assert isinstance(destination, Point)
    #     self.vel = self.pos.movement_to(destination)
    #
    # def set_destination(self, dest):
    #     self.set_destination(dest, self.speed)
    #
    # def rotate(self, angle):  # in radians
    #     self.course = self.course + angle

    def turn(self, time_elapsed):  # time in seconds
        self._velocity += self._acceleration * time_elapsed
        self._position += self._velocity * time_elapsed



