import math
import unittest
import random
from itertools import count

def db(reference, level):
    return math.log10(level / reference) * 10


def attenuation(source_level, db):
    return source_level / (10 ** (db / 10))


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
    return [abs(x) for x in f[1:len(f)/2]]



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

class TestUtil(unittest.TestCase):
    def test_decibels(self):
        self.assertEqual(db(1, 10), 10)
        self.assertEqual(db(3, 30), 10)
        self.assertEqual(db(1, 100), 20)
        self.assertEqual(db(5, 500), 20)
        self.assertEqual(db(1, 1000), 30)
        self.assertAlmostEqual(db(1, 2), 3.0103)
        self.assertAlmostEqual(db(1, 20), 13.0103)
        self.assertAlmostEqual(db(1, 30), 14.771212547196624)
        self.assertAlmostEqual(db(1, 50), 16.9897)
        self.assertAlmostEqual(db(1, 90), 19.54242509439325)

    def test_attenuation(self):
        self.assertEqual(attenuation(10, 10), 1)
        self.assertEqual(attenuation(100, 20), 1)
        self.assertEqual(attenuation(100, 10), 10)
        self.assertEqual(attenuation(1000, 30), 1)
        self.assertAlmostEqual(attenuation(2, 3.0103), 1)


if __name__ == '__main__':
    unittest.main()