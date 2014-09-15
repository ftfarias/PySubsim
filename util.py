# -*- coding: utf-8 -*-
import collections
import math
import random
import unittest


def normalize_angle360(angle):
    # return the angle between 0 and 360 (in radians)
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle


def normalize_angle180(angle):
    # return the angle between -180 and + 180 (in radians)
    while angle < -math.pi/2:
        angle += 2 * math.pi
    while angle >= math.pi:
        angle -= 2 * math.pi
    return angle


def abs_angle_to_bearing(angle):
    #return round(math.degrees(normalize_angle360(angle - (math.pi/2))))
    #return round(math.degrees(angle))
    return round(math.degrees(normalize_angle360(angle)))



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
    def __init__(self):
        self.n = 0
        self.mean = 0
        self.M2 = 0

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


    def test_bands_equal(self):
        b1 = Bands([1.0, 2.0, 3.0, 4.0])
        b2 = Bands([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(b1, b2)

    def test_bands_mul(self):
        b1 = Bands([1.0, 2.0, 3.0, 4.0]) * 2
        b2 = Bands([2.0, 4.0, 6.0, 8.0])
        self.assertEqual(b1, b2)

if __name__ == '__main__':
    unittest.main()



