# -*- coding: utf-8 -*-
import unittest

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


    def get_acceleration(self):
        return self._acceleration.length

    def _set_acceleration(self, value):
        self._acceleration.length = value

    acceleration = property(get_acceleration, _set_acceleration, None, "Acceleration")

    def get_course(self):
        return self._velocity.angle

    def set_course(self, angle):
        '''
        :param angle: new angle in radians
        :return: none
        '''
        angle = normalize_angle_2pi(angle)
        self._velocity.angle = angle
        self._acceleration.angle = self._velocity.angle  # assumes the rotation also changes the acceleration

    course = property(get_course, set_course, "Course")

    def get_bearing(self):
        return self._velocity.bearing

    bearing = property(get_bearing, None, "Bearing")


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
    def rotate(self, angle):  # in radians
        self.course = self.course + angle

    def turn(self, time_elapsed):  # time in seconds
        self._velocity += self._acceleration * time_elapsed
        self._position += self._velocity * time_elapsed

    def __str__(self):
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
        m1 = MovableNewtonObject()
        m1.turn(20)
        self.assertEqual(m1.position, Point(0, 0))

    def test_mov_vel_contant(self):
        m1 = MovableNewtonObject()
        m1._velocity = Point(1, 2)
        m1.turn(20)
        self.assertAlmostEqual(m1.position.x, 20)
        self.assertAlmostEqual(m1.position.y, 40)

    def test_mov_vel_contant2(self):
        m1 = MovableNewtonObject()
        m1._velocity = Point(1, 2)
        m1.turn(10)
        self.assertAlmostEqual(m1.position.x, 10)
        self.assertAlmostEqual(m1.position.y, 20)
        m1.turn(5)
        m1.turn(5)
        self.assertAlmostEqual(m1.position.x, 20)
        self.assertAlmostEqual(m1.position.y, 40)

    def test_mov_speed(self):
        m1 = MovableNewtonObject()
        m1._velocity = Point(4, 3)
        self.assertEqual(m1.speed, 5)

    def test_mov_speed2(self):
        m1 = MovableNewtonObject()
        m1._velocity = Point(3, -4)
        self.assertEqual(m1.speed, 5)

    def test_mov_speed3(self):
        m1 = MovableNewtonObject()
        m1._velocity = Point(6, 8)
        self.assertEqual(m1.speed, 10)


if __name__ == '__main__':
    unittest.main()
