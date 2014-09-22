# -*- coding: utf-8 -*-
from util import Bands
from physic import Point, MovableNewtonObject
from sub import Submarine
import random
import math
import unittest
import datetime
from sound import Decibel, db, simple_sound_absortion_by_sea
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

KNOWN_TYPES = {
    # Symbol for map display
    # Number of blades. ex: [4,5] four or five blades.
    # Sonar Bands
    # bands:  50, 100, 300, 500, 1000, 2000, 15000, 20000




    # f = 12 Hz - @2-5 kHz for “whale songs”, SL up to 188 dB
    'Whale': {'symbol': 'B',
         'blades': [0, 0],
         'bands': Bands([0]),
         'noise': [20, 30],
         'deep': [0, 100]},

    # generate intense broadband noise, f = 1-10 kHz, SL =60-90 dB
    'Snapping Shrimp': {'symbol': 'B',
         'blades': [0, 0],
         'bands': Bands([0]),
         'noise': [10, 15],
         'deep': [10, 15]},


    # Merchant Vessels/Tankers: Typically three or four blades; noisy;
    # often maintains predictable course.
    'Large Merchant Vessel':
        {'symbol': 'M',
         'blades': [3, 4],
         'bands': Bands([0]),
         'noise': [70, 80],
         'deep': [0, 0]},

    'Small Merchant Vessel':
        {'symbol': 'M',
         'blades': [3, 4],
         'bands': Bands([0]),
         'noise': [50, 70],
         'deep': [0, 0]},

    # Warships: Typically four or five-bladed propellers; quieter, smoother
    # sound than merchant ships; possibly unpredictable course changes.

    'Destroyer':
        {'symbol': '^',
         'blades': [4, 5],
         'bands': Bands([0]),
         'noise': [20, 30],
         'deep': [0, 0]},

    'Warship':
        {'symbol': '^',
         'blades': [4, 5],
         'bands': Bands([0]),
         'noise': [20, 45],
         'deep': [0, 0]},

    # Submarines: Five, six or seven-bladed propellers;
    # very quiet when submerged and at low speed; unpredictable course changes.
    'Akula':
        {'symbol': 'S',
         'blades': [7, 7],
         'bands': Bands([0]),
         'noise': [5, 15],
         'deep': [68, 300]},

    '688':
        {'symbol': 'S',
         'blades': [6, 6],
         'bands': Bands([0]),
         'noise': [5, 15],
         'deep': [68, 300]},

    # Fishing Vessels/Trawlers/Pleasure Craft: Three- or four-bladed propellers;
    # noisy; erratic courses and speeds, frequently stopping and starting.

    'Fishing Boat':
        {'symbol': 'F',
         'blades': [3, 4],
         'bands': Bands([0]),
         'noise': [50, 65],
         'deep': [0, 0]},

    'Fishing Ship':
        {'symbol': 'F',
         'blades': [3, 4],
         'bands': Bands([0]),
         'noise': [65, 85],
         'deep': [0, 0]},

    'Torpedo':
        {'symbol': 'T',
         'blades': [5, 5],
         'bands': Bands([20000]),
         'noise': [65, 85],
         'deep': [0, 0]},

}


def symbol_for_type(kind):
    if kind is None:
        return '?'
    elif kind not in KNOWN_TYPES:
        return '<UNKNOW TYPE>'
    else:
        return KNOWN_TYPES[kind]['symbol']


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


class SeaObject():
    def __init__(self, kind):
        self.details = None
        self.kind = kind
        self.sonar_bands = KNOWN_TYPES[kind]['bands']
        blades_range = KNOWN_TYPES[kind]['blades']
        self.blades = random.randint(blades_range[0], blades_range[1])
        deep_range = KNOWN_TYPES[kind]['deep']
        self.deep = random.randint(deep_range[0], deep_range[1])
        noise_range = KNOWN_TYPES[kind]['noise']
        self.noise = random.randint(noise_range[0], noise_range[1])

    def get_pos(self):
        return Point(0, 0)

    def turn(self, time_elapsed):
        pass

    def get_sonar_bands(self):
        return self.sonar_bands

    def get_deep(self):
        return self.deep;

    def self_noise(self):
        return self.noise

    def __str__(self):
        return "{k}: pos:{pos} deep={deep} noise={noise}  blades={bl} {det}".format(k=self.kind,
            deep=self.get_deep(), noise=self.self_noise(), pos=self.get_pos(), bl=self.blades, det=self.details)


class SimpleSeaObject(SeaObject, MovableNewtonObject):
    def __init__(self, kind, pos):
        SeaObject.__init__(self, kind)
        MovableNewtonObject.__init__(self)
        self.pos = pos

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):
        MovableNewtonObject.turn(self,time_elapsed)

    def set_destination(self, course, speed):
        self.vel = Point(1,1)
        self.speed = speed
        self.course = course


class SeaSurfaceShip(SeaObject):  # adapter para class SHIP
    def __init__(self, ship, kind='Surface Ship'):
        SeaObject.__init__(self, kind)
        self.ship = ship

    def add_waypoint(self, dest):
        self.ship.add_waypoint(dest)

    def get_pos(self):
        return self.ship.get_pos()

    def get_deep(self):
        return 0;

    def turn(self, time_elapsed):
        self.ship.turn(time_elapsed)


class SeaSubmarine(SeaObject):
    def __init__(self, sub):
        SeaObject.__init__(self, sub.kind)
        assert isinstance(sub, Submarine)
        self.sub = sub

    def get_pos(self):
        p = self.sub.get_pos()
        assert isinstance(p, Point)
        return self.sub.get_pos()

    def get_deep(self):
        return self.sub.get_deep()

    def self_noise(self):
        return self.sub.self_noise()

    def turn(self, time_elapsed):
        self.sub.turn(time_elapsed)

        # def get_sonar_bands(self):
        #    return self.sonar_bands


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
        bio = SimpleSeaObject("Whale", pos)
        bio.deep = random.randint(30, 100)
        bio.set_destination(random.randint(0,359), 1)
        self.objects.append(bio)

    def create_warship(self, pos=None, ship_type=None):
        t = ['Destroyer', 'Warship']
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        if ship_type is None:
            ship_type = t[random.randint(0, len(t) - 1)]
        ship = SimpleSeaObject(ship_type, pos)
        ship.set_destination(random.randint(0, 359), random.randint(5, 15))
        self.objects.append(ship)

    def create_fishing(self, pos=None, ship_type=None):
        t = ['Fishing Boat', 'Fishing Ship']
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        if ship_type is None:
            ship_type = t[random.randint(0, len(t) - 1)]
        ship = SimpleSeaObject(ship_type, pos)
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
        return db(random.gauss(20, 2))

    def sound_attenuation(self, freq, deep):
        return db(simple_sound_absortion_by_sea(freq, deep))

    def passive_scan(self, sub, time_elapsed):
        logger.debug("--- Passive scan ---")
        sub_pos = sub.get_pos()
        assert isinstance(sub_pos, Point)
        result = []
        background_noise = self.get_background_noise() + sub.self_noise()
        logger.debug("background_noise {0}".format(background_noise))
        for i, obj in enumerate(self.objects):
            obj_pos = obj.get_pos()
            dist = obj_pos.distance_to(sub_pos)
            logger.debug("{i}: dist:{dist:5.2f}  obj:{obj}".format(i=i, dist=dist, obj=obj))
            #if dist > 15:  # hard limit for object detection.
            #    continue
            assert isinstance(obj.get_pos(), Point)
            object_sound = obj.self_noise()
            deep_in_km = sub.get_deep() / 3280  # 3280 feet = 1 km
            attenuation = self.sound_attenuation(freq=100, deep=deep_in_km) * 1.8  # in db/km * 1.8 = db/knot
            logger.debug("{i}: object_sound:{os}  deep_in_km:{deep}  attenuation:{at}/nm".format(i=i, os=object_sound, deep=deep_in_km, at=attenuation))
            #received_sound = object_sound - (attenuation * dist)
            #if not isinstance(object_sound, Decibel):
            #    received_sound = db(received_sound)
            #signal_to_noise = received_sound / background_noise
            signal_to_noise = 1
            deep = obj.get_deep()

            bands = (obj.get_sonar_bands())  # add_noise
            # .add_noise(0.1*dist)
            range = sub_pos.distance_to(obj_pos)
            bearing = sub_pos.angle_to(obj_pos)
            # Scan Result
            r = ScanResult(i)
            r.signal_to_noise = signal_to_noise
            r.range = range
            r.bearing = bearing
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

