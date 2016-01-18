# -*- coding: utf-8 -*-
import collections
import math
import random
import unittest
from sound.sound import sum_of_decibels
import copy

def angles(num_angles):
    step = 360 / num_angles
    return [(a*step, (a+1)*step) for a in xrange(num_angles)]


def angles_to_unicode(angle):
    def interval(a, direction):
        return direction-22.5 <= a < direction+22.5

    if angle is None:
        return u'\u2219'.encode(self.strcode)
    elif interval(angle, 45):
        return u'\u2197'
    elif interval(angle, 90):
        return u'\u2192'
    elif interval(angle, 135):
        return u'\u2198'
    elif interval(angle, 180):
        return u'\u2193'
    elif interval(angle, 225):
        return u'\u2199'
    elif interval(angle, 270):
        return u'\u2190'
    elif interval(angle, 315):
        return u'\u2196'
    else:
        return u'\u2191'

def shift(l, n):
    return l[n:] + l[:n]

def normalize_angle_2pi(angle):
    # return the angle between 0 and 2*pi (in radians)
    while angle < 0:
        angle += 2 * math.pi
    return angle % (math.pi * 2)


def normalize_angle_pi(angle):
    # return the angle between -180 and + 180 (in radians)
    while angle < -math.pi:
        angle += 2 * math.pi
    while angle >= math.pi:
        angle -= 2 * math.pi
    return angle


def angle_to_bearing(angle):
    angle_deg = math.degrees(angle)
    return (90.0 - angle_deg) % 360

def bearing_to_angle(bearing):
    angle_rad = math.radians(90 - bearing)
    return normalize_angle_pi(angle_rad)


def limits(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value


HERTZ_LABEL = ['Hz', 'KHz', 'MHz', 'GHz']
def int_to_hertz(value, str_format = "{0}{1}"):
    scale = 0
    while value >= 1000:
        value /= 1000.0
        scale += 1

    #if isinstance(value, Decibel):
    #    value = value.value

    value = round(value, 1)
    return str_format.format(value, HERTZ_LABEL[scale])

    # if scale == 0 and value < 1:
    #     return "{0:0.1f}{1}".format(value,HERTZ_LABEL[scale])
    # else:
    #     return "{0:0.0f}{1}".format(value,HERTZ_LABEL[scale])


class Bands():
    def __init__(self, bands={}):
        self.bands = bands.copy()

    def add(self, freq, level):
        self.bands[freq] = level
        return Bands(self.bands)

    def add_random(self, freq_interval, level_interval, times=1):
        result = Bands(bands=self.bands)
        for _ in xrange(times):
            level = random.randint(level_interval[0], level_interval[1])
            freq = random.randint(freq_interval[0], freq_interval[1])
            result = result.add(freq, level)
        return result

    def get_freqs(self):
        return self.bands.keys()

    def get_freq_level(self):
        return self.bands.copy().items()

    def total_level(self):
        return sum_of_decibels(self.bands.values())

    def filter(self, min_level):
        for k, v in self.bands.items():
            if v < min_level:
                del self.bands[k]
        return Bands(self.bands.copy())


    #def add_noise(self, noise):
    #    return Bands([max(0, b + random.gauss(0, noise)) for b in self.bands])

    #def log(self):
    #    return [math.log10(b) for b in self.bands]

    # def likelihood(self, other):
    #     var = 0.0
    #     for r, m in zip(self.normalize(), other.normalize()):
    #         var += ((m - r) ** 2)
    #     # print ("ref:{0} mensured:{1} {2} chi:{3}".format(ref_band,measured_band,n, chi))
    #     return math.sqrt(var)


    def __str__(self):
        #return self.bands
        if self.bands:
            return " | ".join(["{0}db @ {1}".format(l, int_to_hertz(f)) for f,l in self.bands.items()])
        else:
            return "<no bands>"


def calc_bands(ref_bands, factor, noise):
    result = []
    for b in ref_bands:
        result.append(1.0 * b * factor + random.gauss(0, noise * factor))
    return result


class OnLineMean():
    def __init__(self):
        self.n = 0
        self.mean = 0
        self.M2 = 0

    def add_variable(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.M2 += delta * (x - self.mean)

    def remove_variable(self, x):
        self.n -= 1
        delta = x - self.mean
        self.mean -= delta / self.n
        self.M2 -= delta * (x - self.mean)

    def update_variable(self, old_x, new_x):
        delta = new_x - old_x
        dold = old_x - self.mean
        mean = self.mean + delta / self.n
        dnew = new_x - mean
        self.M2 += delta * (dold + dnew)

    def get_variance(self):
        return self.M2 / (self.n - 1)


def knots_to_yards(knots):
    return knots * 2025.371828521


def yards_to_knots(yards):
    return yards / 2025.371828521

def knots_to_meters(knots):
    return knots * 1852.0

def meters_to_knots(yards):
    return yards / 1852.0

def feet_to_meters(feet):
    return feet / 3.2808399

def meters_to_feet(meters):
    return meters * 3.2808399


def linreg(X, Y):
    """
    Returns coefficients to the regression line "y=ax+b" from x[] and
    y[].  Basically, it solves
        Sxx a + Sx b = Sxy
         Sx a +  N b = Sy
    where Sxy = \sum_i x_i y_i, Sx = \sum_i x_i, and Sy = \sum_i y_i.  The
    solution is
        a = (Sxy N - Sy Sx)/det
        b = (Sxx Sy - Sx Sxy)/det
    where det = Sxx N - Sx^2.  In addition,
        Var|a| = s^2 |Sxx Sx|^-1 = s^2 | N  -Sx| / det
           |b|       |Sx  N |          |-Sx Sxx|
        s^2 = {\sum_i (y_i - \hat{y_i})^2 \over N-2}
            = {\sum_i (y_i - ax_i - b)^2 \over N-2}
            = residual / (N-2)
        R^2 = 1 - {\sum_i (y_i - \hat{y_i})^2 \over \sum_i (y_i - \mean{y})^2}
            = 1 - residual/meanerror

    It also prints to <stdout> few other data,
        N, a, b, R^2, s^2,
    which are useful in assessing the confidence of estimation.
    """
    from math import sqrt

    if len(X) != len(Y):  raise ValueError, 'unequal length'

    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in map(None, X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x * x
        Syy = Syy + y * y
        Sxy = Sxy + x * y
    det = Sxx * N - Sx * Sx
    a, b = (Sxy * N - Sy * Sx) / det, (Sxx * Sy - Sx * Sxy) / det

    meanerror = residual = 0.0
    for x, y in map(None, X, Y):
        meanerror += (y - Sy / N) ** 2
        residual += (y - a * x - b) ** 2
    RR = 1 - residual / meanerror
    ss = residual / (N - 2)
    Var_a, Var_b = ss * N / det, ss * Sxx / det

    print "y=ax+b"
    print "N= %d" % N
    print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N - 2, sqrt(Var_a))
    print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N - 2, sqrt(Var_b))
    print "R^2= %g" % RR
    print "s^2= %g" % ss

    return a, b


def time_length_to_str(seconds):
    if seconds < 60:
        return "{0}s".format(seconds)
    elif 3600 > seconds >= 60:
        minutes = int(math.floor(seconds/60))
        seconds -= minutes * 60
        return "{0}m{1}".format(minutes,seconds)
    else:
        hours = int(math.floor(seconds/3600))
        seconds -= hours * 3600
        minutes = int(math.floor(seconds/60))
        seconds -= minutes * 60
        return "{0}h{1}".format(hours, minutes)

def ascii_color(text, r, g, b):
    return '\033[38;2;{r};{g};{b}m{s}'.format(r=r, b=b, g=g, s=text)

def ascii_gray(text, gray_level):
    return ascii_color(text, gray_level, gray_level, gray_level)

def ascii_reset():
    return '\033[30m'

class Alternation(object):
    def __init__(self, state=False, initial_counter=1):
        self.state = state
        self.counter = initial_counter

    def turn(self, time_elapsed):
        self.counter -= time_elapsed
        if self.counter <= 0:
            if self.state:
                self.state = False
                self.counter = random.randint(1, 10)+random.randint(1, 10)+random.randint(1, 10)
            else:
                self.state = True
                self.counter = random.gauss(8, 5)+random.gauss(12, 5)


class Deployable(object):
    STOP = "Stopped"
    DEPLOY = 'Deploying'
    RETRIEVE = 'Retrieving'
    BROKE = 'Broke'

    def __init__(self, size, deploy_rate, inicial_deployed_size=0):
        self.state = self.STOP
        self.deployed_size = inicial_deployed_size
        self.total_size = size
        self.deploy_rate = deploy_rate

    def turn(self, time_elapsed):
        if self.state == self.DEPLOY:
            self.deployed_size += self.deploy_rate * time_elapsed
            if self.deployed_size >= self.total_size:
                self.deployed_size = self.total_size
                self.state = self.STOP

        elif self.state == self.RETRIEVE:
            self.deployed_size -= self.deploy_rate * time_elapsed
            if self.deployed_size <= 0:
                self.deployed_size = 0
                self.state = self.STOP

    def deploy(self):
        if self.state != self.BROKE:
            self.state = self.DEPLOY

    def stop(self):
        if self.state != self.BROKE:
            self.state = self.STOP

    def retrieve(self):
        if self.state != self.BROKE:
            self.state = self.RETRIEVE

    def broke(self):
        self.state = self.BROKE
        self.deployed_size = 0

    def percent_deployed(self):
        return self.deployed_size/self.total_size

    def __str__(self):
        return "{0} ({1})".format(self.state, self.deployed_size)


def cosine_interpolate(y1, y2, m):
    mu2 = (1.0-math.cos(m*math.pi))/2.0
    return (y1*(1-mu2)+y2*mu2)


class TestUtil(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()


