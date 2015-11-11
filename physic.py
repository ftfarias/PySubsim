# -*- coding: utf-8 -*-
import math
import random
import unittest
from point import Point

from util import normalize_angle360, abs_angle_to_bearing, limits

class MovableNewtonObject(object):
    def __init__(self):
        self.pos = Point(0, 0)
        self.vel = Point(0, 0)
        self.accel = Point(0, 0)
        self.friction = 0

    def get_speed(self):
        return self.vel.length

    def _set_speed(self, value):
        self.vel.length = value

    speed = property(get_speed, _set_speed, None, "Speed")

    def set_acceleration(self, value):
        self.accel.length = value

    def get_acceleration(self):
        return self.accel.length

    acceleration = property(get_acceleration, set_acceleration, None, "Acceleration")

    def get_course(self):
        return self.vel.angle

    def new_course(self, angle):
        self.vel.angle = angle
        self.accel.angle = self.vel.angle  # assumes the rotation also changes the acceleration

    course = property(get_course, new_course, "Course")

    def set_speed(self, new_speed):
        self.nav.speed = new_speed

    # Destination

    def set_destination(self, destination, speed):
        assert isinstance(destination, Point)
        self.vel = self.pos.movement_to(destination) * speed

    def set_destination(self, dest):
        self.set_destination(dest, self.speed)

    def rotate(self, angle):
        self.course = normalize_angle360(self.course + angle)

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):  # time in seconds
        self.vel += self.accel * time_elapsed
        self.vel.length -= self.vel.length * self.friction
        if self.rudder != 0:
            self.rotate(self.rudder * time_elapsed)
        self.pos += self.vel * time_elapsed

    def __str__(self):
        return "pos:{p}  vel:{v}(r={vt:.1f};{va:.0f}˚)  accel:{a}(r={at:.1f};{aa:.0f}˚)  course:{c:.1f}, rudder:{rudder}".format(
            p=self.pos,
            v=self.vel,
            vt=self.speed,
            va=abs_angle_to_bearing(self.vel.angle),
            a=self.accel,
            at=self.acceleration,
            aa=abs_angle_to_bearing(self.accel.angle),
            c=abs_angle_to_bearing(self.course),
            rudder=abs_angle_to_bearing(self.rudder))


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.p1 = Point(1, 2)
        self.p2 = Point(3, 4)

    def test_equal(self):
        self.assertEqual(Point(4, 6), Point(4, 6))

    def test_equal2(self):
        self.assertEqual(Point(4.0, 6.0), Point(4, 6))

    def test_add(self):
        self.assertEqual(self.p1 + self.p2, Point(4, 6))

    def test_sub(self):
        self.assertEqual(self.p1 - self.p2, Point(-2, -2))

    def test_mul(self):
        self.assertEqual(self.p1 * 10, Point(10, 20))
        self.assertEqual(self.p2 * 10, Point(30, 40))

    def test_mu2(self):
        self.assertEqual(self.p1 * Point(3, 5), Point(3, 10))
        self.assertEqual(self.p2 * Point(5, 3), Point(15, 12))

    def test_distance(self):
        self.assertEqual(Point(0, 0).distance_to(Point(3, 4)), 5)
        self.assertEqual(Point(4, 3).distance_to(Point(0, 0)), 5)

    def test_angle_to(self):
        p1 = Point(0, 0)
        p2 = Point(-5, 0)  # Left
        self.assertEqual(p1.angle_to(p2), 0)

        p1 = Point(0, 0)
        p2 = Point(0, -1)  # top
        self.assertEqual(p1.angle_to(p2), math.pi / 2)

        p1 = Point(0, 0)
        p2 = Point(5, 0)  # right
        self.assertEqual(p1.angle_to(p2), math.pi)

        p1 = Point(0, 0)
        p2 = Point(0, 1)  # bottom
        self.assertEqual(p1.angle_to(p2), -1.0 * math.pi / 2)

    def test_movement_to1(self):
        p1 = Point(0, 0)
        p2 = Point(-5, 0)
        self.assertAlmostEqual(p1.movement_to(p2).x, -1.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, 0.000)

    def test_movement_to2(self):
        p1 = Point(0, 0)
        p2 = Point(5, 0)
        self.assertAlmostEqual(p1.movement_to(p2).x, 1.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, 0.000)

    def test_movement_to3(self):
        p1 = Point(1, 1)
        p2 = Point(1, 5)
        self.assertAlmostEqual(p1.movement_to(p2).x, 0.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, 1.000)

    def test_movement_to4(self):
        p1 = Point(10, 10)
        p2 = Point(10, 5)
        self.assertAlmostEqual(p1.movement_to(p2).x, 0.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, -1.000)

    def test_mov_stopped(self):
        m1 = MovableNewtonObject()
        m1.turn(20)
        self.assertEqual(m1.pos, Point(0, 0))

    def test_mov_vel_contant(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(1, 2)
        m1.turn(20)
        self.assertAlmostEqual(m1.pos.x, 20)
        self.assertAlmostEqual(m1.pos.y, 40)

    def test_mov_vel_contant2(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(1, 2)
        m1.turn(10)
        self.assertAlmostEqual(m1.pos.x, 10)
        self.assertAlmostEqual(m1.pos.y, 20)
        m1.turn(5)
        m1.turn(5)
        self.assertAlmostEqual(m1.pos.x, 20)
        self.assertAlmostEqual(m1.pos.y, 40)

    def test_mov_speed(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(4, 3)
        self.assertEqual(m1.speed, 5)

    def test_mov_speed2(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(3, -4)
        self.assertEqual(m1.speed, 5)

    def test_mov_speed3(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(6, 8)
        self.assertEqual(m1.speed, 10)


if __name__ == '__main__':
    unittest.main()
