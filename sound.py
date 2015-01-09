# -*- coding: utf-8 -*-
import math
import random
from itertools import count
import unittest
from linear_scale import linear_scaler

class Decibel(object):
    def __init__(self, db=0, ratio=1):
        self.value = float(db) + (math.log10(ratio) * 10)

    def __add__(self, other):
        if isinstance(other, Decibel):
            return Decibel(ratio=abs(self) + abs(other))
        else:
            return other * abs(self)

    def __sub__(self, other):
        if isinstance(other, Decibel):
            return Decibel(ratio=abs(self) - abs(other))
        else:
            return other / abs(self)

    # like: 100 - 3*db = 50  (3db ~= half)
    def __rsub__(self, other):
        if isinstance(other, Decibel):
            return Decibel(ratio=abs(self) - abs(other))
        else:
            return other / abs(self)


    def __mul__(self, other):
        if isinstance(other, Decibel):
            return Decibel(db=self.value + other.value)
        else:
            return Decibel(db=self.value * other)

    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, Decibel):
            return Decibel(db=self.value - other.value)
        else:
            return Decibel(ratio=abs(self) / other)

    def __abs__(self):
        return self.abs()

    def abs(self):
        return 10 ** (self.value / 10)

    def __lt__(self, other):
        if isinstance(other, Decibel):
            return self.value < other.value
        else:
            return self.value < other

    def __le__(self, other):
        if isinstance(other, Decibel):
            return self.value <= other.value
        else:
            return self.value <= other

    def __eq__(self, other):
        if isinstance(other, Decibel):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        if isinstance(other, Decibel):
            return self.value != other.value
        else:
            return self.value != other

    def __ge__(self, other):
        if isinstance(other, Decibel):
            return self.value >= other.value
        else:
            return self.value >= other

    def __gt__(self, other):
        if isinstance(other, Decibel):
            return self.value > other.value
        else:
            return self.value > other

    def add_noise(self, noise_level_db):
        return self + db(random.gauss(0, noise_level_db))

    def __str__(self):
        return "{0:3.3f}db".format(self.value)

    __repr__ = __str__


def db(db=0, ratio=1):
    return Decibel(db=db, ratio=ratio)


def nextpow2(i):
    """
    Find 2^n that is equal to or greater than.
    """
    n = 2
    while n < i: n = n * 2
    return n


def bitrev(x):
    """
    Return bit-reversed list, whose length is assumed to be 2^n:
    eg. 0111 <--> 1110 for N=2^4.
    """
    N, x = len(x), x[:]
    if N != nextpow2(N): raise ValueError, 'N is not power of 2'
    for i in range(N):
        k, b, a = 0, N >> 1, 1
        while b >= a:
            if b & i: k = k | a
            if a & i: k = k | b
            b, a = b >> 1, a << 1
        if i < k:  # important not to swap back
            x[i], x[k] = x[k], x[i]
    return x


def fft(x, sign=-1):
    """
    FFT using Cooley-Tukey algorithm where N = 2^n.  The choice of
    e^{-j2\pi/N} or e^{j2\pi/N} is made by 'sign=-1' or 'sign=1'
    respectively.  Since I prefer Engineering convention, I chose
    'sign=-1' as the default.

    FFT is performed as follows:
    1. bit-reverse the array.
    2. partition the data into group of m = 2, 4, 8, ..., N data points.
    3. for each group with m data points,
        1. divide into upper half (section A) and lower half (section B),
        each containing m/2 data points.
        2. divide unit circle by m.
        3. apply "butterfly" operation
            |a| = |1  w||a|	or	a, b = a+w*b, a-w*b
            |b|   |1 -w||b|
        where a and b are data points of section A and B starting from
        the top of each section, and w is data points along the unit
        circle starting from z = 1+0j.
    FFT ends after applying "butterfly" operation on the entire data array
    as whole, when m = N.
    """
    from cmath import pi, exp

    N, W = len(x), []
    for i in range(N):  # exp(-j...) is default
        W.append(exp(sign * 2j * pi * i / N))
    x = bitrev(x)
    m = 2
    while m <= N:
        for s in range(0, N, m):
            for i in range(m / 2):
                n = i * N / m
                a, b = s + i, s + i + m / 2
                x[a], x[b] = x[a] + W[n % N] * x[b], x[a] - W[n % N] * x[b]
        m = m * 2
    return x


def ifft(X):
    """
    Inverse FFT with normalization by N, so that x == ifft(fft(x)) within
    round-off errors.
    """
    N, x = len(X), fft(X, sign=1)  # e^{j2\pi/N}
    for i in range(N):
        x[i] = x[i] / float(N)
    return x


def spectrum(wave):
    f = fft(wave)
    return [abs(x) for x in f[1:len(f) / 2]]


def sine_wave(frequency=440.0, framerate=44000, amplitude=1):
    if amplitude > 1.0:
        amplitude = 1.0
    if amplitude < 0.0:
        amplitude = 0.0
    frequency = float(frequency)
    return (amplitude * math.sin(2.0 * math.pi * frequency * (float(i) / framerate)) for i in
            count(0))


def sine_wave_array(size, frequency=440.0, framerate=44000, amplitude=1):
    wave = sine_wave(frequency=frequency, framerate=framerate, amplitude=amplitude)
    return [wave.next() for _ in xrange(size)]


def white_noise(amplitude=0.5):
    return (float(amplitude) * random.uniform(-1, 1) for _ in count(0))

#sound_absortion_freq = [0, 500, 1000, 2000, 5000, 10000, 20000]
#sound_absortion_att = [0, 0.03, 0.07, 0.14, 0.41, 1.3, 4.6]
_simple_sound_absortion_1 = linear_scaler([0,2000],[0,0.14])
_simple_sound_absortion_2 = linear_scaler([2000,5000],[0.14,0.41])
_simple_sound_absortion_3 = linear_scaler([5000,10000],[0.41,1.3])
_simple_sound_absortion_4 = linear_scaler([10000,20000],[1.3,4.6])
_simple_sound_absortion_5 = linear_scaler([20000,100000],[4.6,1000])
def simple_sound_absortion_by_sea(freq, deep):
    if freq <= 2000:
        return _simple_sound_absortion_1(freq)
    elif freq <= 5000:
        return _simple_sound_absortion_2(freq)
    elif freq <= 10000:
        return _simple_sound_absortion_3(freq)
    elif freq <= 20000:
        return _simple_sound_absortion_4(freq)
    elif freq <= 100000:
        return _simple_sound_absortion_5(freq)
    else:
        return 1000


def sound_absortion_by_sea(freq, deep, temperature=10.0, salinity=35.0, pH=8.0):
    """
    http://resource.npl.co.uk/acoustics/techguides/seaabsorption/
    calculation of absorption according to:
	Ainslie & McColm, J. Acoust. Soc. Am., Vol. 103, No. 3, March 1998
	// f frequency (kHz)
	// T Temperature (degC)
	// S Salinity (ppt)
	// D Depth (km)
	// pH Acidity

	The Ainslie and McColm formula retains accuracy to within 10% of the
	 Francois and Garrison model between 100 Hz and 1 MHz for the following range of oceanographic conditions:

    -6 < T < 35 °C	(S = 35 ppt, pH=8, D = 0 km)
    7.7 < pH < 8.3	(T = 10 °C, S = 35 ppt, D = 0 km)
    5 < S < 50 ppt	(T = 10 °C, pH = 8, D = 0 km)
    0 < D < 7 km	(T = 10 °C, S = 35 ppt, pH = 8)
    :return Total absorption (dB/km)
    """

    freq = freq / 1000.0 # converts from KHz to Hz
    deep = deep / 1000.0 # convert meters to km

    kelvin = 273.1  # for converting to Kelvin (273.15)  # Measured ambient temp
    t_kel = kelvin + temperature

    # Boric acid contribution
    a1 = 0.106 * math.exp((pH - 8.0) / 0.56);
    p1 = 1.0;
    f1 = 0.78 * math.sqrt(salinity / 35.0) * math.exp(temperature / 26.0);
    boric = 1.0 * (a1 * p1 * f1 * freq * freq) / (freq * freq + f1 * f1);

    # MgSO4 contribution
    a2 = 0.52 * (salinity / 35.0) * (1 + temperature / 43.0);
    p2 = math.exp(-deep / 6);
    f2 = 42.0 * math.exp(temperature / 17.0);
    mgso4 = 1.0 * (a2 * p2 * f2 * freq * freq) / (freq * freq + f2 * f2);

    # Pure water contribution
    a3 = 0.00049 * math.exp(-(temperature / 27.0 + deep / 17.0));
    p3 = 1.0;
    h2o = 1.0 * a3 * p3 * freq * freq;

    # Total absorption (dB/km)
    alpha = boric + mgso4 + h2o;

    return alpha;


class TestUtil(unittest.TestCase):
    def test_decibels(self):
        self.assertAlmostEqual(abs(db(db=3.01029995664)), abs(db(ratio=2)))

        self.assertAlmostEqual(abs(db(db=10)), abs(db(ratio=10)))
        self.assertAlmostEqual(abs(db(db=20)), abs(db(ratio=100)))
        self.assertAlmostEqual(abs(db(db=30)), abs(db(ratio=1000)))

        self.assertAlmostEqual(abs(db(db=13.0103)), abs(db(ratio=20)), 3)
        self.assertAlmostEqual(abs(db(db=14.771212547196624)), abs(db(ratio=30)), 3)
        self.assertAlmostEqual(abs(db(db=16.9897)), abs(db(ratio=50)), 3)
        self.assertAlmostEqual(abs(db(db=19.54242509439325)), abs(db(ratio=90)), 3)

    def test_decibels_sum(self):
        self.assertAlmostEqual(db(60) + db(60), db(63.01029995664), 5)

    def test_decibels_abs(self):
        self.assertAlmostEqual(abs(db(db=0)), 1)
        self.assertAlmostEqual(abs(db(db=10)), 10)
        self.assertAlmostEqual(abs(db(db=20)), 100)

    def test_attenuation(self):
        self.assertAlmostEqual(100 - (3.0103 * db(1)), 50, 4)


if __name__ == '__main__':
    unittest.main()