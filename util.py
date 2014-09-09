# -*- coding: utf-8 -*-
import collections
import math
import random
import unittest


def normalize_angle(angle):
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle


class Point():
    """ Point class represents and manipulates x,y coords. """

    def __init__(self, x=0, y=0, z=0):
        """ Create a new point at x, y """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
            return "({0: .3f}, {1: .3f}, {1: .3f})".format(self.x, self.y, self.z)

    def __add__(a, b):
        if isinstance(b, Point):
            return Point(a.x + b.x, a.y + b.y, a.z + b.z )
        elif hasattr(b, "__getitem__"):
            return Point(a.x + b[0], a.y + b[1], a.z + b[2])
        else:
            return Point(a.x + b, a.y + b, a.z + b)

    def __sub__(a, b):
        if isinstance(b, Point):
            return Point(a.x - b.x, a.y - b.y, a.z - b.z )
        elif hasattr(b, "__getitem__"):
            return Point(a.x - b[0], a.y - b[1], a.z - b[2])
        else:
            return Point(a.x - b, a.y - b, a.z - b)

    def __mul__(a, b):
        if isinstance(b, Point):
            return Point(a.x * b.x, a.y * b.y, a.z * b.z)
        elif hasattr(b, "__getitem__"):
            return Point(a.x * b[0], a.y * b[1], a.z * b[2])
        else:
            return Point(a.x * b, a.y * b, a.z * b)

    __rmul__ = __mul__

    def __imul__(self, b):
        if isinstance(b, Point):
            self.x *= b.x
            self.y *= b.y
            self.z *= b.z
        elif (hasattr(b, "__getitem__")):
            self.x *= b[0]
            self.y *= b[1]
            self.z *= b[2]
        else:
            self.x *= b
            self.y *= b
            self.z *= b
        return self


    def __div__(a, b):
        if isinstance(b, Point):
            return Point(a.x / b.x, a.y / b.y, a.z / b.z)
        else:
            return Point(a.x / b, a.y / b, a.z / b)

    def __eq__(a,b):
        return a.x == b.x and a.y == b.y and a.z == b.z

    def distance_to(self, other):
        """ Compute my distance """
        p = self - other
        return math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z)
        #return math.hypot(p.x, p.y, p.z)

    def distance2_to(self, other):
        """
        Distance using only x and y
        :param other:
        :return: Distance using only x and y
        """
        p = self - other
        return math.hypot(p.x, p.y)

    def add_gaussian_noise(self, x, y=None, z=None):
        if y is None:
            y = x
        if z is None:
            z = x
        n_x = self.x + random.gauss(0, x)
        n_y = self.y + random.gauss(0, y)
        n_z = self.z + random.gauss(0, z)
        return Point(n_x, n_y, n_z)

    def movement_to(self, other):
        angle = other.angle_to(self)
        return Point(math.cos(angle),math.sin(angle))

    def get_length_sqrd(self):
        return self.x**2 + self.y**2

    def get_length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __setlength(self, value):
        length = self.get_length()
        self.x *= value/length
        self.y *= value/length

    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")

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
        p = self - other
        if p.get_length_sqrd() == 0:
            return 0
        return math.atan2(p.y, p.x)

    def get_angle(self):
        if self.get_length_sqrd() == 0:
            return 0
        return math.atan2(self.y, self.x)

    def __setangle(self, angle_degrees):
        self.x = self.length
        self.y = 0
        self.rotate(angle_degrees)

    angle = property(get_angle, __setangle, None, "gets or sets the angle of a vector")

    def dot(self, other):
        return float(self.x*other[0] + self.y*other[1] + self.z*other[2])

    def __getstate__(self):
        return [self.x, self.y, self.z]

    def __setstate__(self, dict):
        self.x, self.y, self.z = dict

class MovableNewtonObject:
    def __init__(self):
        self.pos = Point(0, 0, 0)
        self.vel = Point(0, 0, 0)
        self.accel = Point(0, 0, 0)
        self.friction = 0
        self.course = 0
        self.rudder = 0

    def turn(self, time_elapsed):
        self.vel += self.accel * time_elapsed
        self.vel.length -= self.vel.length * self.friction
        self.rotate(self.rudder * time_elapsed)
        self.pos += self.vel * time_elapsed
        self.course = self.vel.angle

    def speed(self):
        return self.vel.length

    def course(self):
        return self.course

    def new_course(self, angle):
        self.course = angle
        self.vel.angle = angle

    def set_destination(self, dest, speed):
        assert isinstance(dest, Point)
        self.vel = self.pos.movement_to(dest) * speed

    def rotate(self, angle):
        self.course = normalize_angle(self.course + angle)
        self.vel.rotate(self.course)

    def __str__(self):
        return "pos:{0}  vel:{1}  accel:{2}  course:{3}".format(self.pos,
                                                                self.vel,
                                                                self.accel,
                                                                math.degrees(self.course))
def abs_angle_to_bearing(angle):
    return normalize_angle(angle - (math.pi/2))


def limits(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value


class Bands():
    def __init__(self, bands=[0.0]*10):
        self.bands = bands

    def __add__(self, other):
        result = []
        for a,b in zip(self, other):
            result.append(a+b)
        return result

    def __sub__(self, other):
        result = []
        for a,b in zip(self, other):
            result.append(a-b)
        return result

    def __mul__(self, other):
        return Bands([b*other for b in self.bands])

    def __div__(self, other):
        return Bands([b/other for b in self.bands])

    def __eq__(self, other):
        return self.bands == other.bands

    def add_noise(self, noise):
        return Bands([max(0, b+random.gauss(0, noise)) for b in self.bands])

    def normalize(self):
        total = sum(self.bands)
        return Bands([b/total for b in self.bands])

    def likelihood(self, other):
        var = 0.0
        for r, m in zip(self.normalize(), other.normalize()):
            var += ((m - r) ** 2)
        #print ("ref:{0} mensured:{1} {2} chi:{3}".format(ref_band,measured_band,n, chi))
        return math.sqrt(var)

    def __str__(self):
        return " | ".join(["{0:3.1f}".format(b) for b in self.bands])


class BandsAcumulator():
    def __init__(self):
        self.bands = [OnLineMean() for _ in xrange(10)]

    def normalize(self):
        total = sum([b.mean for b in self.bands])
        return Bands([b.mean/total for b in self.bands])

    def passive(self):
        return Bands(self.bands[0:5])

    def active(self):
        return Bands(self.bands[5:10])

    def likelihood(self, other):
        var = 0.0
        for r,m in zip(self.normalize(), other.normalize()):
            var += ((m - r) ** 2)
        #print ("ref:{0} mensured:{1} {2} chi:{3}".format(ref_band,measured_band,n, chi))
        return math.sqrt(var)

    def __str__(self):
        return " ".join(["{0:5}".format(b) for b in self.bands])

def calc_bands(ref_bands, factor, noise):
    result = []
    for b in ref_bands:
        result.append(1.0*b*factor+random.gauss(0, noise*factor))
    return result


class OnLineMean():
    n = 0
    mean = 0
    M2 = 0

    def add_variable(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta/self.n
        self.M2 += delta*(x - self.mean)

    def remove_variable(self, x):
        self.n -= 1
        delta = x - self.mean
        self.mean -= delta/self.n
        self.M2 -= delta*(x - self.mean)

    def update_variable(self, old_x, new_x):
        delta = new_x - old_x
        dold = old_x - self.mean
        mean = self.mean + delta/self.n
        dnew = new_x - mean
        self.M2 += delta*(dold + dnew)

    def get_variance(self):
        return self.M2/(self.n-1)



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

    def test_bands_equal(self):
        b1 = Bands([1.0, 2.0, 3.0, 4.0])
        b2 = Bands([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(b1, b2)

    def test_bands_mul(self):
        b1 = Bands([1.0, 2.0, 3.0, 4.0]) * 2
        b2 = Bands([2.0, 4.0, 6.0, 8.0])
        self.assertEqual(b1, b2)

    def test_mov_stopped(self):
        m1 = MovableNewtonObject()
        m1.turn(20)
        self.assertEqual(m1.pos, Point(0, 0, 0))

    def test_mov_vel_contant(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(1, 2, -3)
        m1.turn(20)
        self.assertEqual(m1.pos, Point(20, 40, -60))

    def test_mov_vel_contant2(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(1, 2, -3)
        m1.turn(10)
        self.assertEqual(m1.pos, Point(10, 20, -30))
        m1.turn(5)
        m1.turn(5)
        self.assertEqual(m1.pos, Point(20, 40, -60))

    def test_mov_speed(self):
        m1 = MovableNewtonObject()
        m1.vel = Point(4, 3, 0)
        self.assertEqual(m1.speed(), 5)
        m1.vel = Point(0, 3, 4)
        self.assertEqual(m1.speed(), 5)
        m1.vel = Point(6, 0, 8)
        self.assertEqual(m1.speed(), 10)

if __name__ == '__main__':
    unittest.main()

