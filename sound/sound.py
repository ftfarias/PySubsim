# -*- coding: utf-8 -*-
import math
import random
from itertools import count
import logging

from util.linear_scale import linear_scaler

logger = logging.getLogger("subsim.sound")

# REFERENCE_FREQS = [0.1, 1, 10, 30, 50, 100, 300, 500, 1000, 3000, 5000, 10000, 15000, 20000]


'''
Reference bands:

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000



NL - noise level


'''


def db_to_power(db):
    return 10 ** (db / 10.0)


def power_to_db(power):
    return 10.0 * math.log10(power)


def sum_of_decibels(db_lists):
    powers = [10 ** (db / 10) for db in db_lists]
    total_power = sum(powers)
    return 10 * math.log10(total_power)


def total_broadband_level(mean, freq_low, freq_high):
    """
    :param mean: average intensity in DB
    :param freq_low: lower band frequency
    :param freq_high: higher band frequency
    :return: the total DBS for the band level
    """
    return mean + ( 10 * math.log10(freq_high - freq_low))


class Sound(object):
    REFERENCE_BANDS = []
    for i in range(1, 10):
        REFERENCE_BANDS.append(i)
    for i in range(1, 10):
        REFERENCE_BANDS.append(i * 10)
    for i in range(1, 11):
        REFERENCE_BANDS.append(i * 100)

    # for i in range(1,1000):
    # REFERENCE_BANDS.append(i)

    NUM_BANDS = len(REFERENCE_BANDS) - 1

    REFERENCE_BANDS_CENTRAL_FREQ = []
    for i in range(NUM_BANDS):
        REFERENCE_BANDS_CENTRAL_FREQ.append(math.sqrt(REFERENCE_BANDS[i] * REFERENCE_BANDS[i + 1]))

    REFERENCE_BANDS_BANDWIDTH = []
    for i in range(NUM_BANDS):
        REFERENCE_BANDS_BANDWIDTH.append(REFERENCE_BANDS[i + 1] - REFERENCE_BANDS[i])


    def __init__(self):
        # assert isinstance(sub, Submarine)
        self.values = [-100.0] * self.NUM_BANDS


    def total_band(self, band_index):
        # total_power = db_to_power( self.values[band_index] ) * self.REFERENCE_BANDS_BANDWIDTH[band_index]
        # return power_to_db(total_power)
        return self.values[band_index] + (10 * math.log10(self.REFERENCE_BANDS_BANDWIDTH[band_index]))


    def total_decibels(self):
        p = [self.total_band(i) for i in range(self.NUM_BANDS)]
        return sum_of_decibels(p)


    def get_bands(self):
        result = {}
        for i in range(self.NUM_BANDS):
            freq = self.REFERENCE_BANDS_CENTRAL_FREQ[i]
            value = self.values[i]
            result[freq] = value
        return result


    def filter(self, filter_function):
        # def filter(frequence, value): return new_value
        for i in range(self.NUM_BANDS):
            freq = self.REFERENCE_BANDS_CENTRAL_FREQ[i]
            current_value = self.values[i]
            self.values[i] = filter_function(freq, current_value)


    def logdecay(self, start_db, start_freq, stop_db, stop_freq):
        start_freq_log = math.log10(start_freq)
        frequence_span = math.log10(stop_freq) - start_freq_log
        decibel_span = stop_db - start_db
        scale_factor = float(decibel_span) / float(frequence_span)
        for i in range(self.NUM_BANDS):
            if self.REFERENCE_BANDS[i] >= start_freq and self.REFERENCE_BANDS[i] <= stop_freq:
                freq = math.log10(self.REFERENCE_BANDS_CENTRAL_FREQ[i])
                v = start_db + (freq - start_freq_log) * scale_factor
                self.values[i] = v

    def add_logdecay(self, start_db, start_freq, stop_db, stop_freq):
        start_freq_log = math.log10(start_freq)
        frequence_span = math.log10(stop_freq) - start_freq_log
        decibel_span = stop_db - start_db
        scale_factor = float(decibel_span) / float(frequence_span)
        for i in range(self.NUM_BANDS):
            if self.REFERENCE_BANDS[i] >= start_freq and self.REFERENCE_BANDS[i] <= stop_freq:
                freq = math.log10(self.REFERENCE_BANDS_CENTRAL_FREQ[i])
                v = start_db + (freq - start_freq_log) * scale_factor
                self.values[i] = sum_of_decibels([self.values[i], v])


    def add_cosine(self, start_db, start_freq, stop_db, stop_freq):
        # add a sound using a cosine interpolator
        start_freq_log = math.log10(start_freq)
        frequence_span = math.log10(stop_freq) - start_freq_log
        decibel_span = stop_db - start_db
        scale_factor = float(decibel_span) / float(frequence_span)
        for i in range(self.NUM_BANDS):
            if self.REFERENCE_BANDS[i] >= start_freq and self.REFERENCE_BANDS[i] <= stop_freq:
                freq = math.log10(self.REFERENCE_BANDS_CENTRAL_FREQ[i])
                m = (freq - start_freq_log) / frequence_span  # 0 > m > 1 -> linear between start_freq and stop_freq
                mu2 = (1.0 - math.cos(m * math.pi)) / 2.0 # cosine interpolator
                v = (start_db * (1 - mu2) + stop_db * mu2)  # value in DB
                self.values[i] = sum_of_decibels([self.values[i], v])


    def set_frequency(self, freq, value):
        freq_index = None
        for i in range(self.NUM_BANDS):
            if self.REFERENCE_BANDS[i] == freq:
                freq_index = i
                break

        if freq_index == None:
            logger.warning("band not found at sound.set_frequency({},{})".format(freq, value))
        else:
            self.values[freq_index] = value
        return self

    def add_frequencs(self, freqs_dict):
        for i in range(self.NUM_BANDS):
            freq = self.REFERENCE_BANDS[i]
            if freq in freqs_dict.keys():
                self.values[freq] = sum_of_decibels([freqs_dict[freq], self.values[freq]])
        return self


    def add_direct(self, other_sound):
        for i in range(self.NUM_BANDS):
            self.values[i] += other_sound.values[i]


    def print_values(self):
        for i in range(self.NUM_BANDS):
            if self.values[i] > 0:
                print(
                    "[{}] {:2,} - {:2,}: \t Center: {:.2f} \t 1 Hz Power: {:.2f} db \t Total band power: {:.2f} db".format(
                        i,
                        self.REFERENCE_BANDS[i],
                        self.REFERENCE_BANDS[i + 1],
                        self.REFERENCE_BANDS_CENTRAL_FREQ[i],
                        self.values[i],
                        self.total_band(i)
                    ))

        print("Total DB: {:,}".format(self.total_decibels()))

    def min_max_band_values(self):
        max = 0
        min = 10000
        for i in range(self.NUM_BANDS):
            v = self.values[i]
            if v > 0 and v > max:
                max = v
            if v > 0 and v < min:
                min = v
        return min, max

    def v_to_unicode(self,value):
        if value <= 0:
            s = u"_".encode("UTF8")
        elif value <= 1:
            s = u"\u2581".encode("UTF8")
        elif value <= 2:
            s = u"\u2582".encode("UTF8")
        elif value <= 3:
            s = u"\u2583".encode("UTF8")
        elif value <= 4:
            s = u"\u2584".encode("UTF8")
        elif value <= 5:
            s = u"\u2585".encode("UTF8")
        elif value <= 6:
            s = u"\u2586".encode("UTF8")
        elif value <= 7:
            s = u"\u2587".encode("UTF8")
        else: # value > 7
            s = u"\u2588".encode("UTF8")
        return s

    DEFAULT_LINEAR_ASCII = linear_scaler([50, 140], [0, 8])

    def ascii(self, linear_scale=None):
        if linear_scale is None:
            min,max = self.min_max_band_values()
            linear_scale = linear_scaler([min, max], [0, 8])
        s = []
        for i in range(self.NUM_BANDS):
            value = linear_scale(self.values[i])
            s.append(self.v_to_unicode(value))

        return "".join(s)

    DEFAULT_LINEAR_ASCII_2_LINES = linear_scaler([50, 140], [0, 16])
    # <=  0 -> _ or " "
    # <=  1 -> 1/8
    # <=  2 -> 2/8
    # <=  3 -> 3/8
    # <=  4 -> 4/8
    # <=  5 -> 5/8
    # <=  6 -> 6/8
    # <=  7 -> 7/8
    # <=  8 -> 8/8
    # <=  9 -> 8/8 + 1/8
    # <= 10 -> 8/8 + 2/8
    # <= 11 -> 8/8 + 3/8
    # <= 12 -> 8/8 + 4/8
    # <= 13 -> 8/8 + 5/8
    # <= 14 -> 8/8 + 6/8
    # <= 15 -> 8/8 + 7/8
    # <= 16 -> 8/8 + 8/8


    def ascii2lines(self, linear_scale=DEFAULT_LINEAR_ASCII_2_LINES):
        l1 = []
        l2 = []
        for i in range(self.NUM_BANDS):
            value = linear_scale(self.values[i])
            if value >= 8:
                l1.append(u"\u2588".encode("UTF8"))
                l2.append(self.v_to_unicode(value-8))
            else:
                l1.append(self.v_to_unicode(value))
                l2.append(" ")

        return ("".join(l1), "".join(l2))

    def add_noise(self, stddev):
        # stddev = standard deviation
        s = Sound()
        for i in range(self.NUM_BANDS):
            s.values[i] = self.values[i] + random.gauss(0,stddev)
        return s


#
# s = Sound()
# s.logdecay(140,50,120,500)
# s = Sound().set_frequency(10,20).set_frequency(50,100)
# s.print_values()
# def f(freq, value):
# return value / freq
# s.filter(f)
# s.print_values()
# print(s.print_symbol())

#
# s = Sound()
# s.logdecay(140,1,50,1000)
# print(s.ascii2lines)

##############################

# s1 = Sound()
# s1.set_frequency(10,60)
# s1.set_frequency(20,50)
# s1.set_frequency(30,40)
# s2 = Sound()
# s2.set_frequency(20,0)
# s2.set_frequency(30,30)
# s2.set_frequency(40,35)
# s1.add_direct(s2)
# s1.print_values()

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



