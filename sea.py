# -*- coding: utf-8 -*-
import unittest
import logging
import datetime

from sea_object import *
from util import feet_to_meters, knots_to_meters
from linear_scale import linear_scaler
import sound


logger = logging.getLogger("subsim")

"""
A novice asked the Master: “Here is a programmer that never designs,
documents or tests his programs. Yet all who know him consider him
one of the best programmers in the world. Why is this?”

The Master replies: “That programmer has mastered the Tao. He has gone
beyond the need for design; he does not become angry when the system
crashes, but accepts the universe without concern. He has gone beyond
the need for documentation; he no longer cares if anyone else sees his
code. He has gone beyond the need for testing; each of his programs
are perfect within themselves, serene and elegant, their purpose self-evident.
Truly, he has entered the mystery of Tao.”
"""


class ScanResult:
    def __init__(self, object_idx):
        self.object_idx = object_idx
        self.signal_to_noise = 0
        self.bearing = 0
        self.range = 0
        self.deep = 0
        self.blades = 0
        self.bands = None

    def __str__(self):
        return "ScanResult idx={id} snt={snt} bearing={b} range={r} deep={deep} blades={bl} band={band}". \
            format(id=self.object_idx, snt=self.signal_to_noise, b=self.bearing, r=self.range,
                   deep=self.deep, bl=self.blades, band=self.bands)


class Sea:
    def __init__(self):
        self.time = datetime.datetime(2010, 05, 05, random.randint(0, 23), random.randint(0, 59), 0)
        self.counter = 0
        self.objects = {}
        self.ids_collection = range(1000, 9999)
        random.shuffle(self.ids_collection)
        self.conditions = 'Calm'
        # background_noise_factor should be 1 < background_noise_factor < 1.75
        self.background_noise_factor = 1.2
        # limits below because sound absortion formula
        self.temperature = random.randint(-60, 150) / 10.0  # Celsius, -6 < T < 35
        self.salinity = float(random.randint(30, 35))  # 5 < S < 50 ppt
        self.ph = 1.0 * random.randint(77, 83) / 10  # 7.7 < pH < 8.3

    def initialize(self):
        pass

    def get_unique_id(self):
        return self.ids_collection.pop()

    def add_object(self, obj):
        # self.objects.append(obj)
        self.objects[self.get_unique_id()] = obj

    def turn(self, time_elapsed):  # time_elapsed in hours
        self.time = self.time + datetime.timedelta(seconds=time_elapsed * 3600)
        for obj in self.objects.values():
            obj.turn(time_elapsed)


    # def background_noise_for_freq_min_max(self, freq):
    # # using Wenz (1962)
    #     # http://www.dosits.org/science/soundsinthesea/commonsounds
    #     # Min and Max values done by linear aproximation
    #     logfreq = math.log10(freq)
    #
    #     # for minimum value:
    #     # 1 -> 10 Hz, 5 -> 10KHz
    #     # > x = c(1,5)
    #     # > y = c(85,20)
    #     # > l = lm(y ~ x)
    #     # Coefficients:
    #     # (Intercept)            x
    #     # 101.25       -16.25
    #     min_value = 101.25 + (-16.25 * logfreq)
    #
    #     # > y_max = c(140,60)
    #     # > l = lm(y_max ~ x)
    #     # Coefficients:
    #     # (Intercept)            x
    #     # 160          -20
    #     max_value = 160.0 + (-20.0 * logfreq)
    #     return min_value, max_value


    background_noise_scaler = linear_scaler([0, 4], [80, 20])

    def background_noise_for_freq(self, freq):
        # using Wenz (1962)
        # http://www.dosits.org/science/soundsinthesea/commonsounds
        # Min and Max values done by linear aproximation
        logfreq = math.log10(freq)
        base_value = self.background_noise_scaler(logfreq)

        # background_noise_factor should be 1 < background_noise_factor < 1.75

        value = (base_value * self.background_noise_factor) + random.gauss(0, 2)

        return value

    def get_background_noise(self):
        return self.background_noise_for_freq(50)
        #return [self.background_noise_for_freq(i) for i in sound.REFERENCE_FREQS]

    # def get_background_noise(self):
    # return db(random.gauss(80, 2))

    def sound_absortion_by_sea(self, freq, deep, temperature, salinity, pH):
        """
        freq in Hertz
        deep in feet
        temp in degC
        salinity in ppt

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

        freq = freq / 1000.0  # converts from KHz to Hz
        deep = feet_to_meters(deep) / 1000.0  # convert feet to km

        # kelvin = 273.1  # for converting to Kelvin (273.15)  # Measured ambient temp
        # t_kel = kelvin + temperature

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

        return alpha  # in db/km;


    def spherical_spreading_loss(self, dist):
        # dist in meters
        # http://www.dosits.org/science/advancedtopics/spreading/
        # Spherical spreading describes the decrease in level when a sound wave
        # propagates away from a source uniformly in all directions.
        return 20 * math.log10(dist)  # decibels

    def cylindrical_spreading_loss(self, dist):
        # dist in meters
        # http://www.dosits.org/science/advancedtopics/spreading/
        # Sound cannot propagate uniformly
        # in all directions from a source in the ocean forever.
        # Beyond some range the sound will hit the sea surface or sea floor.
        # A simple approximation for spreading loss in a medium with upper and
        # lower boundaries can be obtained by assuming that the sound is distributed
        # uniformly over the surface of a cylinder having a radius equal to the range r
        # and a height H equal to the depth of the ocean
        return 10 * math.log10(dist)  # decibels


    # def passive_sonar_scan(self, sub, sonar):
    # logger.debug("--- Passive sonar scan ---")
    # sub_pos = sub.get_pos()
    #     assert isinstance(sub_pos, Point)
    #     result = []  # list of ScanResult


    def passive_scan(self, sub, sonar):
        logger.debug("--- Passive scan ---")
        logger.debug("Sub: {0}".format(sub))
        logger.debug("Sonar: {0}".format(sonar))
        sub_pos = sub.get_pos()
        assert isinstance(sub_pos, Point)
        result = {}
        # background_noise = self.get_background_noise() + sub.self_noise()
        #logger.debug("background_noise {0}".format(background_noise))
        for idx, obj in self.objects.items():
            obj_pos = obj.get_pos()
            # skips the sub itself
            if sub_pos == obj_pos:
                continue
            range_in_knots = obj_pos.distance_to(sub_pos)  # in knots/miles
            # if range > 15:  # hard limit for object detection.
            #     continue
            assert isinstance(obj.get_pos(), Point)
            object_bands = obj.get_bands()
            assert isinstance(object_bands, Bands)
            logger.debug("** Examining: {i}: dist:{dist:5.2f}  obj:{obj}  type:{ty}"
                         "  obj bands: {b}".format(i=idx, dist=range_in_knots,
                                                   obj=obj,
                                                   ty=type(obj),
                                                   b=object_bands))

            received_bands = self.calculate_dectect_frequences(sub, sonar, obj, range_in_knots)
            logger.debug("received_bands: {0}".format(received_bands))

            # total_received_sound = sum([i[1] for i in received_bands])
            # total_received_noise = sum([i[2] for i in received_bands])
            # signal_to_noise = total_received_sound - total_received_noise
            # logger.debug("total_received_sound : {0}".format(total_received_sound))
            # logger.debug("total_received_noise : {0}".format(total_received_noise))
            # logger.debug("signal_to_noise : {0}".format(signal_to_noise))

            # consolidate bands in a total detected signal-to-noise value
            total_detected_signal_to_noise = 0
            detected_bands = {}
            for band in received_bands:
                freq = band[0]
                signal = band[1]
                noise = band[2]
                stn = signal - noise - sonar.detection_threshold
                if stn > 0:
                    total_detected_signal_to_noise += stn
                    detected_bands[freq] = stn

            logger.debug("total_detected_signal_to_noise : {0}".format(total_detected_signal_to_noise))

            #if not isinstance(object_sound, Decibel):
            #    received_sound = db(received_sound)
            # logger.debug("{i}: signal_to_noise:{stn}".format(i=i, stn=signal_to_noise))
            if total_detected_signal_to_noise > 0:
                # error: greater the signal_to_noise, less the error
                if total_detected_signal_to_noise > 10 + sonar.detection_threshold:
                    error = 0.0001  # means 0.1% in measure
                else:
                    # the error moves from 5% to 1% in a exponencial decay
                    error = 0.0001 + 0.0004 * math.exp(-0.5 * total_detected_signal_to_noise)
                # it's divided by 3 because in a gaussian 99% of time we are inside 3 sigmas...
                # so the error is "max" error for 99% of measures
                error /= 3
                deep = obj.get_deep()
                # .add_noise(0.1*dist)
                bearing = sub_pos.bearing_to(obj_pos)
                #bearing = obj_pos.bearing_to(sub_pos)
                # Scan Result
                r = ScanResult(idx)
                r.signal_to_noise = total_detected_signal_to_noise
                r.blades = 0
                r.distance = range_in_knots * random.gauss(1, error)
                r.bearing = bearing * random.gauss(1, error)
                r.deep = deep * random.gauss(1, error)
                r.bands = detected_bands
                logger.debug("scan_result: {0}".format(r))
                # result.append(r)
                result[idx] = r
        return result  # def passive_scan(self, sub, sonar):


    def calculate_dectect_frequences(self, sub, sonar, obj, range_in_knots):
        received_bands = []
        for freq, source_level in obj.get_bands().get_freq_level():
            range_in_meters = knots_to_meters(range_in_knots)
            deep = sub.actual_deep

            ocean_deep = 2000  # in meters
            half_ocean_deep = ocean_deep / 2
            if range_in_meters < half_ocean_deep:
                spreading_loss = self.spherical_spreading_loss(range_in_meters)
            else:
                # mix of spherical and cylindrical losses
                # spherical losses up to half_ocean_deep + cylindrical
                # http://www.dosits.org/science/advancedtopics/spreading/
                # http://www.fas.org/man/dod-101/navy/docs/es310/SNR_PROP/snr_prop.htm
                spreading_loss = (10 * math.log10(range_in_meters)) + (10 * math.log10(half_ocean_deep))

            absorption = self.sound_absortion_by_sea(float(freq), float(deep),
                                                     temperature=self.temperature,
                                                     salinity=self.salinity,
                                                     pH=self.ph) * range_in_meters / 1000

            transmission_loss = spreading_loss + absorption
            sub_noise_level = sub.self_noise(freq)
            sea_noise_level = self.background_noise_for_freq(freq)
            total_noise = sound.sum_of_decibels([sub_noise_level, sea_noise_level])
            receiving_array_gain = sonar.array_gain(freq)  # AG
            adicional_losses = 0

            received_sound = source_level - transmission_loss \
                             + receiving_array_gain - adicional_losses

            stn = received_sound - total_noise

            received_bands.append((freq, received_sound, total_noise))
            #received_bands = received_bands.add(freq, received_sound)


            logger.debug(
                "* freq:{f}  source level:{sl}  deep:{deep}".format(
                    f=freq, deep=deep,
                    sl=source_level))
            logger.debug(
                "spreading_loss:{spl} absorption:{at} sea_noise:{sean} sub_noise:{subn}".format(
                    at=absorption,
                    sean=sea_noise_level,
                    subn=sub_noise_level,
                    spl=spreading_loss))

            logger.debug(
                "receiving_array_gain:{gain}  transmission_loss:{tl}".format(
                    gain=receiving_array_gain,
                    tl=transmission_loss))

            logger.debug(
                "total_noise:{tn}  received_sound:{rs} stn:{stn}".format(
                    tn=total_noise,
                    rs=received_sound,
                    stn=stn))
        return received_bands

    def pulse(self, ship):
        pass

    def explosion(self, pos):
        # weapon type
        pass

    def __str__(self):
        return "Time: {0}".format(self.time.strftime("%d/%m/%Y %H:%M:%S"))

    def debug(self):
        print('------ SEA DEBUG ------')
        print(self)
        for obj in self.objects.values():
            print (obj)
            print ('')
        print('------ END OF SEA DEBUG ------')


class TestUtil(unittest.TestCase):
    class FakeShip():
        def get_pos(self):
            return Point(0, 0)


    def setUp(self):
        self.universe = Sea()
        self.universe.initialize()

    def test_turn(self):
        u = self.universe
        u.turn(1)
        u.turn(0.1)

    def test_scan_passive(self):
        print("test_scan_passive")
        u = self.universe
        # u.create_asteroid(Point(2,1))
        # u.create_asteroid(Point(1,2))
        scan = u.passive_scan(self.FakeShip(), 0.1)
        self.assertEquals(len(scan), 2)
        print ([str(sr) for sr in scan])


if __name__ == '__main__':
    unittest.main()

"""
Source:
Can Russian Strategic
Submarines Survive at Sea?
The Fundamental Limits of
Passive Acoustics
http://scienceandglobalsecurity.org/archive/sgs04miasnikov.pdf



http://fas.org/man/dod-101/sys/ship/deep.htm
The most obvious contribution to the ambient noise is the action occurring on the surface of
the ocean. The greater the size of the waves, the greater the ambient noise contribution. The
waves are driven by the winds, so there is a direct correspondence between the steady wind speed
and the sea state. The greater the wind speed or sea state, obviously the greater the ambient
noise contribution. The frequency of the noise from sea state tends to be greater than 300 Hz.

The second main contribution to ambient noise comes from shipping in general. In regions where
there are many transiting ships, the ambient noise will be increased substantially. This noise,
in contrast to the noise from sea state, will be at low frequency (< 300 Hz).

The third possible ambient noise source is biologics, meaning sea-life. These are as widely
varied as they are unpredictable. One common source is snapping shrimp. Others include whales
and dolphins.
"""
