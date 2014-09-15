# -*- coding: utf-8 -*-
import math
from util import normalize_angle360, abs_angle_to_bearing
import random
import unittest


class Point(object):
    """ Point class represents and manipulates x,y coords. """

    def __init__(self, x=0, y=0):
        """ Create a new point at x, y """
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return "({0:.3f}, {1:.3f})".format(self.x, self.y)

    def __repr__(self):
        return "Point(x={0}, y={1})".format(self.x, self.y)

    def format(self, format_string="({x:.3f}, {y:.3f})"):
        return format_string.format(x=self.x, y=self.y)

    def __add__(a, b):
        if isinstance(b, Point):
            return Point(a.x + b.x, a.y + b.y)
        elif hasattr(b, "__getitem__"):
            return Point(a.x + b[0], a.y + b[1])
        else:
            return Point(a.x + b, a.y + b)

    def __sub__(a, b):
        if isinstance(b, Point):
            return Point(a.x - b.x, a.y - b.y)
        elif hasattr(b, "__getitem__"):
            return Point(a.x - b[0], a.y - b[1])
        else:
            return Point(a.x - b, a.y - b)

    def __mul__(a, b):
        if isinstance(b, Point):
            return Point(a.x * b.x, a.y * b.y)
        elif hasattr(b, "__getitem__"):
            return Point(a.x * b[0], a.y * b[1])
        else:
            return Point(a.x * b, a.y * b)

    __rmul__ = __mul__

    def __imul__(self, b):
        if isinstance(b, Point):
            self.x *= b.x
            self.y *= b.y
        elif (hasattr(b, "__getitem__")):
            self.x *= b[0]
            self.y *= b[1]
        else:
            self.x *= b
            self.y *= b
        return self


    def __div__(a, b):
        if isinstance(b, Point):
            return Point(a.x / b.x, a.y / b.y)
        else:
            return Point(a.x / b, a.y / b)

    def __eq__(a,b):
        return a.x == b.x and a.y == b.y

    def distance_to(self, other):
        """ Compute my distance """
        p = self - other
        return math.hypot(p.x, p.y)

    def distance2_to(self, other):
        """
        Distance using only x and y
        :param other:
        :return: Distance using only x and y
        """
        p = self - other
        return math.hypot(p.x, p.y)

    def add_gaussian_noise(self, x, y=None):
        if y is None:
            y = x
        n_x = self.x + random.gauss(0, x)
        n_y = self.y + random.gauss(0, y)
        return Point(n_x, n_y)

    def movement_to(self, other):
        angle = other.angle_to(self)
        return Point(math.cos(angle),math.sin(angle))

    def get_length_sqrd(self):
        return self.x**2 + self.y**2

    def get_length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def set_length(self, value):
        length = self.get_length()
        if length == 0:
            self.x = value
            self.y = 0
        else:
            self.x *= value/length
            self.y *= value/length

    length = property(get_length, set_length, None, "gets or sets the magnitude of the vector")

    def rotate(self, radians):
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        self.x = x
        self.y = y

    def rotated(self, radians):
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x*cos - self.y*sin
        y = self.x*sin + self.y*cos
        return Point(x, y)

    def angle_to(self, other):
        p = other - self
        if p.get_length_sqrd() == 0:
            return 0
        return math.atan2(p.y, p.x)

    def get_angle(self):
        if self.get_length_sqrd() == 0:
            return 0
        return math.atan2(self.y, self.x)

    def _setangle(self, radians):
        self.x = self.length
        self.y = 0
        self.rotate(radians)

    angle = property(get_angle, _setangle, None, "gets or sets the angle of a vector")

    def dot(self, other):
        return float(self.x*other[0] + self.y*other[1])

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, dict):
        self.x, self.y = dict


class MovableNewtonObject(object):
    def __init__(self):
        self.pos = Point(0, 0)
        self.vel = Point(0, 0)
        self.accel = Point(0, 0)
        self.friction = 0
        self.rudder = 0  # rudder in radians por minute

    def turn(self, time_elapsed):  # time in seconds
        self.vel += self.accel * time_elapsed
        self.vel.length -= self.vel.length * self.friction
        if self.rudder != 0:
            self.rotate(self.rudder * time_elapsed)
        self.pos += self.vel * time_elapsed

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
        self.vel.angle = normalize_angle360(angle)
        self.accel.angle = self.vel.angle  # assumes the rotation also changes the acceleration

    course = property(get_course, new_course)

    def set_destination(self, dest, speed):
        assert isinstance(dest, Point)
        self.vel = self.pos.movement_to(dest) * speed

    def rotate(self, angle):
        #print(self.course)
        self.course = normalize_angle360(self.course + angle)
        #print(self.course)

        #self.vel.rotate(self.course)

    def __str__(self):
        return "pos:{p}  vel:{v}(r={vt:.1f};{va:.0f}˚)  accel:{a}(r={at:.1f};{aa:.0f}˚)  course:{c:.1f}, rudder:{rudder}".format(p=self.pos,
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
        self.assertEqual(Point(4,6), Point(4,6))

    def test_equal2(self):
        self.assertEqual(Point(4.0, 6.0), Point(4, 6))

    def test_add(self):
        self.assertEqual(self.p1+self.p2, Point(4,6))

    def test_sub(self):
        self.assertEqual(self.p1-self.p2, Point(-2,-2))

    def test_mul(self):
        self.assertEqual(self.p1 * 10, Point(10,20))
        self.assertEqual(self.p2 * 10, Point(30,40))

    def test_mu2(self):
        self.assertEqual(self.p1 * Point(3,5), Point(3,10))
        self.assertEqual(self.p2 * Point(5,3), Point(15,12))

    def test_distance(self):
        self.assertEqual(Point(0,0).distance_to(Point(3,4)), 5)
        self.assertEqual(Point(4,3).distance_to(Point(0,0)), 5)

    def test_angle_to(self):
        p1 = Point(0,0)
        p2 = Point(-5,0) # Left
        self.assertEqual(p1.angle_to(p2), 0)

        p1 = Point(0,0)
        p2 = Point(0,-1) # top
        self.assertEqual(p1.angle_to(p2), math.pi/2)

        p1 = Point(0,0)
        p2 = Point(5,0) # right
        self.assertEqual(p1.angle_to(p2), math.pi)

        p1 = Point(0,0)
        p2 = Point(0,1) # bottom
        self.assertEqual(p1.angle_to(p2), -1.0*math.pi/2)

    def test_movement_to1(self):
        p1 = Point(0,0)
        p2 = Point(-5,0)
        self.assertAlmostEqual(p1.movement_to(p2).x, -1.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, 0.000)

    def test_movement_to2(self):
        p1 = Point(0,0)
        p2 = Point(5,0)
        self.assertAlmostEqual(p1.movement_to(p2).x, 1.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, 0.000)

    def test_movement_to3(self):
        p1 = Point(1,1)
        p2 = Point(1,5)
        self.assertAlmostEqual(p1.movement_to(p2).x, 0.000)
        self.assertAlmostEqual(p1.movement_to(p2).y, 1.000)

    def test_movement_to4(self):
        p1 = Point(10,10)
        p2 = Point(10,5)
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
