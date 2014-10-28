from object_types import KNOWN_TYPES
from physic import Point, MovableNewtonObject
from sound import db
from sub import Submarine
import random

def symbol_for_type(kind):
    if kind is None:
        return '?'
    elif kind not in KNOWN_TYPES:
        return '<UNKNOW TYPE>'
    else:
        return KNOWN_TYPES[kind]['symbol']

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

    def get_deep(self):
        return self.deep;

    def self_noise(self):
        return db(db=self.noise + random.gauss(0,2))

    def __str__(self):
        return "{k}: pos:{pos} deep={deep} noise={noise}  blades={bl} bands={bands} {det}".format(k=self.kind,
            deep=self.get_deep(), noise=self.self_noise(), pos=self.get_pos(),
            bl=self.blades, det=self.details, bands=self.sonar_bands)


class MovableSeaObject(SeaObject, MovableNewtonObject):
    def __init__(self, kind, pos):
        SeaObject.__init__(self, kind)
        MovableNewtonObject.__init__(self)
        self.pos = pos

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):
        MovableNewtonObject.turn(self, time_elapsed)

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
        return self.sub.actual_deep

    def self_noise(self):
        return self.sub.self_noise()

    def turn(self, time_elapsed):
        self.sub.turn(time_elapsed)

        # def get_sonar_bands(self):
        #    return self.sonar_bands