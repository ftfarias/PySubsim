# -*- coding: utf-8 -*-
from util import Bands
from physic import Point, MovableNewtonObject
from sub import Submarine
import random
import math
import unittest
import datetime
from sound import Decibel, db, simple_sound_absortion_by_sea, sound_absortion_by_sea
from object_types import KNOWN_TYPES
from sea_object import *


import logging
logger = logging.getLogger()
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
    def __init__(self, sonar_idx):
        self.sonar_idx = sonar_idx
        self.signal_to_noise = 0

        self.bearing = 0
        self.range = 0
        self.deep = 0
        self.blades = 0

        self.bands = [0.0] * 10

    def __str__(self):
        return "ScanResult idx={id} snt={snt} bearing={b} range={r} deep={deep} blades={bl} band={band}".\
            format(id=self.sonar_idx, snt=self.signal_to_noise, b=self.bearing, r=self.range,
                   deep=self.deep, bl=self.blades, band=self.bands)


class Sea:
    def __init__(self):
        self.time = datetime.datetime(2010, 05, 05, random.randint(0, 23), random.randint(0, 59), 0)
        self.counter = 0
        self.objects = []
        self.ids_collection = range(1000, 9999)
        self.temp = 10  # Celsius
        random.shuffle(self.ids_collection)

    def initialize(self):
        pass

    def get_unique_id(self):
        return self.ids_collection.pop()

    def create_biologic(self, pos=None):
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        bio = MovableSeaObject("Whale", pos)
        bio.deep = random.randint(30, 100)
        bio.set_destination(random.randint(0,359), 1)
        logging.debug("Creating random biologic {0}".format(bio))
        self.objects.append(bio)
        return bio

    def create_warship(self, pos=None, ship_type=None):
        t = ['Destroyer', 'Warship']
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        if ship_type is None:
            ship_type = t[random.randint(0, len(t) - 1)]
        ship = MovableSeaObject(ship_type, pos)
        ship.set_destination(random.randint(0, 359), random.randint(5, 15))
        self.objects.append(ship)
        return ship

    def create_fishing(self, pos=None, ship_type=None):
        t = ['Fishing Boat', 'Fishing Ship']
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        if ship_type is None:
            ship_type = t[random.randint(0, len(t) - 1)]
        ship = MovableSeaObject(ship_type, pos)
        ship.set_destination(random.randint(0, 359), random.randint(1, 5))
        self.objects.append(ship)
        return ship

    def add_submarine(self, sub):
        self.objects.append(SeaSubmarine(sub))

    def turn(self, time_elapsed):
        self.time = self.time + datetime.timedelta(seconds=time_elapsed*3600)
        for obj in self.objects:
            obj.turn(time_elapsed)

    def get_background_noise(self):
        return db(random.gauss(40, 2))

    def sound_attenuation(self, freq, deep):
        #return db(db=simple_sound_absortion_by_sea(freq, deep))
        return db(db=sound_absortion_by_sea(freq,deep))

    def passive_scan(self, sub, time_elapsed):
        logger.debug("--- Passive scan ---")
        sub_pos = sub.get_pos()
        assert isinstance(sub_pos, Point)
        result = []
        background_noise = self.get_background_noise() + sub.self_noise()
        logger.debug("background_noise {0}".format(background_noise))
        for i, obj in enumerate(self.objects):
            obj_pos = obj.get_pos()
            # skips the sub itself
            if sub_pos == obj_pos:
                continue
            range = obj_pos.distance_to(sub_pos)
            logger.debug("{i}: dist:{dist:5.2f}  obj:{obj}".format(i=i, dist=range, obj=obj))
            #if dist > 15:  # hard limit for object detection.
            #    continue
            assert isinstance(obj.get_pos(), Point)
            source_level = obj.self_noise()

            deep_in_km = 1.0 * sub.actual_deep / 3280  # 3280 feet = 1 km
            # most part of a sub self-noise is around 30 Hz
            attenuation_per_mile = self.sound_attenuation(freq=30, deep=deep_in_km) * 1.852  # in db/km * 1.8 = db/mile
            transmission_loss = attenuation_per_mile * range  # TL

            received_sound = source_level / transmission_loss

            receiving_array_gain = 0  # AG


            logger.debug("{i}: source level:{sl}  deep_in_km:{deep}  attenuation:{at}/nm * dist = {tat} recived_sound={rs}".format(
                i=i, sl=source_level, deep=deep_in_km,
                at=attenuation_per_mile,
                tat=transmission_loss ,rs=received_sound))
            #if not isinstance(object_sound, Decibel):
            #    received_sound = db(received_sound)
            signal_to_noise = received_sound / background_noise
            logger.debug("{i}: signal_to_noise:{stn}".format(i=i,stn=signal_to_noise))
            if signal_to_noise.value > 1:
                # error: greater the signal_to_noise, less the error
                if signal_to_noise > 10:
                    error = 0.0001 # means 0.1% in measure
                else:
                    # the error moves from 5% to 1% in a exponencial decay
                    error = 0.0001+0.0004*math.exp(-0.5*signal_to_noise.value)
                # it's divided by 3 because in a gaussian 99% of time we are inside 3 sigmas...
                # so the error is "max" error for 99% of measures
                error /= 3
                deep = obj.get_deep()
                bands = obj.sonar_bands
                # .add_noise(0.1*dist)
                bearing = sub_pos.bearing_to(obj_pos)
                #bearing = obj_pos.bearing_to(sub_pos)
                # Scan Result
                r = ScanResult(i)
                r.signal_to_noise = signal_to_noise
                r.blades = obj.blades
                r.range = range + random.gauss(0, error)
                r.bearing = bearing + random.gauss(0, error)
                r.deep = deep
                r.bands = bands
                logger.debug("scan_result: {0}".format(r))
                logger.debug("")
                result.append(r)
        return result

    def pulse(self, ship):
        pass

    def explosion(self, pos):
        # weapon type
        pass

    def __str__(self):
        return "Time: {0}".format(self.time.strftime("%d/%m/%Y %H:%M:%S"))


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
        #        u.create_asteroid(Point(1,2))
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
