# -*- coding: utf-8 -*-
from util import abs_angle_to_bearing, Bands
from physic import Point, MovableNewtonObject
from sub import Submarine
import random
import math
import unittest
import datetime
from ship import SurfaceShip

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
    #
    'Biologic'    : Bands([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    'Small Boat'  : Bands([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    'Surface Ship': Bands([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    'Tank Ship'   : Bands([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    'Submarine'   : Bands([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
}


class ScanResult:
    def __init__(self, sonar_idx):
        self.sonar_idx = sonar_idx
        self.bearing = 0

        self.range = 0
        self.course = 0
        self.speed = 0

        self.deep = 0
        self.bands = [0.0] * 10

    def __str__(self):
        return "({id}) {pos} |{band}| transp:{t}".format(id=self.universe_idx, pos=self.pos,
                                                         band=str(self.bands), t=self.transponder)

class SeaObject():
    def __init__(self, kind):
        self.details = None
        self.kind = kind
        self.sonar_bands = KNOWN_TYPES[kind]

    def get_pos(self):
        return Point(0, 0)

    def turn(self, time_elapsed):
        pass

    def get_sonar_bands(self):
        return self.sonar_bands

    def get_deep(self):
        return 0;

    def __str__(self):
        return "SeaObj: pos:{pos} ({t}) {det}".format(pos=self.get_pos(), t=self.kind, det=self.details)

class SimpleSeaObject(SeaObject, MovableNewtonObject):
    def __init__(self, kind, pos):
        SeaObject.__init__(self, kind)
        MovableNewtonObject.__init__(self)
        self.pos = pos
        self.deep = 0

    def get_pos(self):
        return self.pos

    def get_deep(self):
        return self.deep

    def set_destination(self, dest, speed):
        assert isinstance(dest, Point)
        self.vel = self.pos.movement_to(dest) * speed

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
    def __init__(self, sub, kind='Submarine'):
        SeaObject.__init__(self, kind)
        assert isinstance(sub, Submarine)
        self.sub = sub

    def get_pos(self):
        p = self.sub.get_pos()
        assert isinstance(p,Point)
        return self.sub.get_pos()

    def get_deep(self):
        return self.sub.get_deep()

    def turn(self, time_elapsed):
        self.sub.turn(time_elapsed)


class Sea:
    def __init__(self):
        self.time = datetime.datetime(2010, 05, 05, random.randint(0, 23), random.randint(0, 59), 0)
        self.counter = 0
        self.objects = []
        self.ids_collection = range(1000, 9999)
        random.shuffle(self.ids_collection)


    def initialize(self):
        pass

    def get_unique_id(self):
        return self.ids_collection.pop()

    def create_biologic(self, pos=None):
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        bio = SimpleSeaObject("Biologic", pos)
        bio.deep = random.randint(30, 100)
        self.objects.append(bio)

    def create_smallboat(self, pos=None):
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        ship = SimpleSeaObject('Small Boat', pos)
        self.objects.append(ship)

    def add_submarine(self, sub):
        self.objects.append(SeaSubmarine(sub))

    def turn(self, time_elapsed):
        self.time = self.time + datetime.timedelta(seconds=time_elapsed)
        for obj in self.objects:
            obj.turn(time_elapsed)

    def passive_scan(self, sub, time_elapsed):
        sub_pos = sub.get_pos()
        assert isinstance(sub_pos, Point)
        result = []
        for i, obj in enumerate(self.objects):
            assert isinstance(obj.get_pos(), Point)
            obj_pos = obj.get_pos()
            dist = obj_pos.distance_to(sub_pos)
            if dist < 15:  # hard limit for object detection.
                bands = (obj.get_sonar_bands()) # add_noise
                 #.add_noise(0.1*dist)
                range = sub_pos.distance_to(obj_pos)
                #print("***")
                #print(sub_pos)
                #print(obj_pos)
                #print(sub_pos.angle_to(obj_pos))
                #print("---")
                bearing = sub_pos.angle_to(obj_pos)
                # Scan Result
                r = ScanResult(i)
                r.range = range
                r.bearing = bearing
                r.course = 0
                r.speed = 0
                r.deep = obj.get_deep()
                r.bands = bands
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
            return Point(0,0)


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
#        u.create_asteroid(Point(2,1))
#        u.create_asteroid(Point(1,2))
        scan = u.passive_scan(self.FakeShip(), 0.1)
        self.assertEquals(len(scan),2)
        print ([str(sr) for sr in scan])

if __name__ == '__main__':
    unittest.main()

