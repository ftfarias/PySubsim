# -*- coding: utf-8 -*-
import math
import cmath
import random
import unittest
from util import util



#############################
#        GAME ANGLES        #
#############################

# (-1, 1)    (0, 1)    (1, 1)
# (-1, 0)  <- 0, 0 ->  (1, 0)
# (-1,-1)    (0,-1)    (1,-1)
#
# 3/4 PI      PI/2      PI/4
#PI/-PI        o         0
#-3/4 PI     -PI/2     -PI/4
#
# NW         North     NE
# West     <- 0, 0 ->  East
# SW         South    SE

#############################
#        USER ANGLES        #
#############################

# (-1, 1)    (0, 1)    (1, 1)
# (-1, 0)  <- 0, 0 ->  (1, 0)
# (-1,-1)    (0,-1)    (1,-1)
#
# NW         North     NE
# West     <- 0, 0 ->  East
# SW         South     SE

# 315   0    45
# 270   o    90
# 225  180   135


class Point(object):
    """ Point class represents and manipulates x,y coords. """

    def __init__(self, x, y=0.0):
        """ Create a new point at x, y """
        if isinstance(x, complex):
            self.v = x
        else:
            self.v = complex(x, y)

    def get_x(self):
        return self.v.real

    def set_x(self, value):
        self.v = complex(value, self.v.imag)

    x = property(get_x, set_x, None, "x value")

    def get_y(self):
        return self.v.imag

    def set_y(self, value):
        self.v = complex(self.v.real, value)

    y = property(get_y, set_y, None, "y value")

    def __str__(self):
        return "({0:.3f}, {1:.3f})".format(self.v.real, self.v.imag)

    def __repr__(self):
        return "Point(x={0}, y={1})".format(self.v.real, self.v.imag)

    def format(self, format_string="({x:.3f}, {y:.3f})"):
        return format_string.format(x=self.v.real, y=self.v.imag)

    def __add__(a, b):
        if isinstance(b, Point):
            return Point(a.v + b.v)
        elif hasattr(b, "__getitem__"):
            return Point(a.v + complex(b[0], b[1]))
        else:
            return Point(a.v + b)

    def __sub__(a, b):
        if isinstance(b, Point):
            return Point(a.v - b.v)
        elif hasattr(b, "__getitem__"):
            return Point(a.v - complex(b[0], b[1]))
        else:
            return Point(a.v - b)

    def __mul__(a, b):
        if isinstance(b, Point):
            return Point(a.v * b.v)
        else:
            return Point(a.v * b)

    __rmul__ = __mul__

    def __truediv__(a, b):
        if isinstance(b, Point):
            return Point(a.v / b.v)
        else:
            return Point(a.v / b)

    def __eq__(a, b):
        return a.v == b.v

    def __abs__(self):
        return abs(self.v)

    def distance_to(self, other):
        """ Compute my distance """
        p = self - other
        return abs(p)

    def add_gaussian_noise(self, x, y=None):
        if y is None:
            y = x
        n_x = self.real + random.gauss(0, x)
        n_y = self.imag + random.gauss(0, y)
        return Point(n_x, n_y)

    def movement_to(self, other):
        angle = self.get_angle_to(other)
        return Point(math.cos(angle), math.sin(angle))


    def get_length(self):
        return abs(self.v)

    def set_length(self, value):
        length = abs(self.v)
        if length <= 0.0001:
            self.v = complex(value, 0)
        else:
            self.v = self.v * (1.0 * value / length)

    length = property(get_length, set_length, None, "gets or sets the magnitude of the vector")

    def unit(self):
        if abs(self.v) == 0:
            return Point(0,0)
        else:
            return Point(self.v / abs(self.v))


    def squared(self):
        return Point(self.v.real**2, self.v.imag**2)


    def get_angle(self):
        """Returns the angle in radians from -pi to +pi  and zero been (1,0) / "east" / 90 user-degrees  """
        if abs(self.v) == 0:
            return 0
        return util.normalize_angle_pi(cmath.phase(self.v))

    def get_angle_to(self, other):
        """Returns the angle in radians from -pi to +pi and zero been (1,0) / "east" / 90 degrees bearing
        :param other: other object
        :returns: angle in radians
        """
        p = other - self
        if abs(p.v) == 0:
            return 0
        return util.normalize_angle_pi(cmath.phase(p.v))

    def set_angle(self, radians):
        new_point = Point(self.length, 0.0)
        return new_point.rotated(radians)


    def get_user_angle_to(self, other):
        """Returns the angle in degrees from 0 to 359 and zero been (0,1) / "north" / 0 degrees bearing
        :param other: other object
        :returns: angle in radians
        """
        p = other - self
        if abs(self.v) == 0:
            return 0
        return p.get_user_angle()

    def get_user_angle(self):
        """Returns the angle in degrees from 0 to 359 and zero been (0,1) / "north" / 0 degrees bearing
        :param other: other object
        :returns: angle in radians
        """
        angle_deg = math.degrees(self.get_angle())
        return (90 - angle_deg) % 360

    def rotated(self, radians):
        cos = math.cos(radians)
        sin = math.sin(radians)
        # print("cos ",cos)
        # print("sin ",sin)
        x = self.v.real * cos - self.v.imag * sin
        y = self.v.real * sin + self.v.imag * cos
        # print("x",x,self.v.real)
        # print("y",y,self.v.imag)
        return Point(x, y)


    def dot(self, other):
        return float(self.x * other[0] + self.y * other[1])

    def __getstate__(self):
        return [self.v.real, self.v.imag]

    def __setstate__(self, dict):
        self.v.real, self.v.imag = dict


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

    def test_distance(self):
        self.assertEqual(Point(0, 0).distance_to(Point(3, 4)), 5)
        self.assertEqual(Point(4, 3).distance_to(Point(0, 0)), 5)
        self.assertEqual(Point(1, 1).distance_to(Point(4, 5)), 5)
        self.assertEqual(Point(5, 4).distance_to(Point(1, 1)), 5)

    def test_length(self):
        self.assertEqual(Point(3, 4).length, 5)
        self.assertEqual(Point(9, 12).length, 15)

    # (-1, 1)    (0, 1)    (1, 1)
    # (-1, 0)  <- 0, 0 ->  (1, 0)
    # (-1,-1)    (0,-1)    (1,-1)
    #
    # 3/4 PI      PI/2      PI/4
    # PI/-PI        o         0
    # -3/4 PI     -PI/2     -PI/4

    def test_angle_to(self):
        p1 = Point(0, 0)
        self.assertEqual(p1.get_angle_to(Point(0, 0)), 0)
        self.assertEqual(p1.get_angle_to(Point(1, 0)), 0)
        self.assertEqual(p1.get_angle_to(Point(1, 1)), math.pi / 4)
        self.assertEqual(p1.get_angle_to(Point(0, 1)), math.pi / 2)
        self.assertEqual(p1.get_angle_to(Point(-1, 1)), 3 * math.pi / 4)
        self.assertEqual(p1.get_angle_to(Point(0, -1)), -math.pi / 2)
        self.assertEqual(p1.get_angle_to(Point(1, -1)), -math.pi / 4)
        self.assertEqual(p1.get_angle_to(Point(-1, -1)), -3 * math.pi / 4)


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

    def test_rotated(self):
        p1 = Point(1, 0)
        self.assertEqual(p1.get_angle(), 0)

        p2 = p1.rotated(math.pi / 2)
        self.assertEqual(p2.get_angle(), math.pi / 2)

        p3 = p2.rotated(math.pi / 2)
        self.assertEqual(p3.get_angle(), math.pi)

    def test_angle(self):
        p1 = Point(8, 0)
        self.assertEqual(p1.get_angle(), 0)

        p2 = p1.set_angle(math.pi / 3)
        self.assertEqual(p2.get_angle(), math.pi / 3)


    def test_change_length(self):
        p1 = Point(4, 3)
        a = p1.get_angle()
        self.assertEqual(p1.length, 5)
        p1.length = 10
        self.assertEqual(p1, Point(8,6) )
        self.assertEqual(a, p1.get_angle() )

    def test_change_length2(self):
        p1 = Point(24, -6)
        a = p1.get_angle()
        p1.length = p1.length * 2
        self.assertEqual(p1, Point(48,-12) )
        self.assertEqual(a, p1.get_angle() )

if __name__ == '__main__':
    unittest.main()
