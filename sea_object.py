import random
from util import Bands
from physic import Point, MovableNewtonObject
from sub_navigation import Navigation
import copy

class SeaObject(object):
    def __init__(self, sea):
        self.details = None
        self.kind = "Sea Object"
        self.bands = Bands()
        self.pos = Point(0, 0)
        self.sea = sea
        self.deep = 0

    def turn(self, time_elapsed):
        pass

    def get_pos(self):
        return self.pos

    def get_deep(self):
        return self.deep;

    def get_bands(self):
        return self.bands
        #return db(db=self.noise + random.gauss(0,2))

    def __str__(self):
        return self.kind
        # return "{k}: pos:{pos} deep={deep} noise={noise} blades={bl} bands={bands} {det}".format(k=self.kind,
        #     deep=self.get_deep(), noise=self.self_noise(), pos=self.get_pos(),
        #     bl=self.blades, det=self.details, bands=self.bands)

class SnappingShrimp(SeaObject):
    # "The snapping shrimp competes with much larger animals
    # such as the Sperm Whale and Beluga Whale for the title of
    # 'loudest animal in the sea'. The animal snaps a specialized claw
    #  shut to create a cavitation bubble that generates acoustic pressures
    # of up to 80 kPa at a distance of 4 cm from the claw. As it extends
    # out from the claw, the bubble reaches speeds of 60 miles per hour
    #  (97 km/h) and releases a sound reaching 218 decibels.[11] The pressure
    #  is strong enough to kill small fish.[12] It corresponds to a
    # zero to peak pressure level of 218 decibels relative to one micropascal
    #  (dB re 1 μPa), equivalent to a zero to peak source level of 190 dB re
    # 1 μPa at the standard reference distance of 1 m. Au and Banks measured
    # peak to peak source levels between 185 and 190 dB re 1 μPa at 1 m, depending
    #  on the size of the claw.[13] Similar values are reported by Ferguson
    # and Cleary.[14] The duration of the click is less than 1 millisecond.


    # Read more: http://www.physicsforums.com

    def __init__(self, sea):
        SeaObject.__init__(self, sea)
        self.snapping = False
        self.counter = random.randint(3, 20) + random.gauss(5, 10)
        # generate intense broadband noise, f = 1-10 kHz, SL = 60-90 dB
        # bands: 5 to 10 high frequence bands
        self.bands = Bands().add_random([1000,10000],[100,160],times=random.randint(5,10))
        self.deep = random.randint(9,20)

    def turn(self, time_elapsed):
        self.counter -= time_elapsed
        if self.snapping:
            if self.counter <= 0:
                # Stop snapping
                self.snapping = False
                self.counter = random.randint(1, 10)+random.randint(1, 10)+random.randint(1, 10)
        else:
            # in silence
            if self.counter <= 0:
                # Stars to snapping
                self.snapping = True
                self.counter = random.gauss(8, 5)+random.gauss(12, 5)

    def get_bands(self):
        if self.snapping:
            return self.bands
        else:
            return Bands()  # Silence


class MovableSeaObject(SeaObject, MovableNewtonObject):
    def __init__(self, sea):
        SeaObject.__init__(self, sea)
        MovableNewtonObject.__init__(self)

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):
        MovableNewtonObject.turn(self, time_elapsed)

    # def set_destination(self, course, speed):
    #     self.vel = Point(1,1)  # just to initialize the vector
    #     self.speed = speed
    #     self.course = course


class Whale(MovableSeaObject):
    # f = 12 Hz - @2-5 kHz for “whale songs”, SL up to 188 dB
    # Swimming: 10 - 20 Hz, 60 to 80 DB
    # Sing: 2Khz - 5 Khz, 120 to 190 DB (AI should handle this later)
    def __init__(self, sea):
        MovableSeaObject.__init__(self, sea)
        self.nav = Navigation(self)
        self.bands_swim = Bands().add_random([10, 20], [60, 80])
        self.bands_swim_sing = copy.deepcopy(self.bands_swim).add_random([2000, 5000], [120,150], times=3)
        self.deep = random.randint(10, 20)
        print ("Swim: "+str(self.bands_swim))
        print ("Sing: "+str(self.bands_swim_sing))
        self.singing = False
        self.counter = random.randint(5, 10)+random.gauss(6, 5)

    def turn(self, time_elapsed):
        MovableSeaObject.turn(self, time_elapsed)
        self.counter -= time_elapsed
        if self.counter <= 0:
            if self.singing:
                self.singing = False
                self.counter = random.randint(10, 5)+random.gauss(5, 5)
            else:
                self.singing = True
                self.counter = random.gauss(10, 3)+5

        if self.nav.destination is None:
            self.nav.destination = Point(random.randint(0,10),random.randint(0,10))
            self.nav.speed = random.random()*20+0.1

    def get_deep(self):
        return self.deep

    def get_pos(self):
        return self.pos

    def get_bands(self):
        if self.singing:
            return self.bands_swim_sing
        else:
            return self.bands_swim


class Ship(MovableSeaObject):
    def __init__(self, sea):
        MovableSeaObject.__init__(self, sea)
        self.navigation = Navigation(self)

    def get_deep(self):
        return 0

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):
        MovableSeaObject.turn(self,time_elapsed)

    def add_waypoint(self, dest):
        self.navigation.add_waypoint(dest)


class ComputerSubmarine(MovableSeaObject):
    def __init__(self, sea):
        MovableSeaObject.__init__(self, sea)
        self.navigation = Navigation(self)
        self.deep = 100

    def get_deep(self):
        return self.deep

    def turn(self, time_elapsed):
        MovableSeaObject.turn(self,time_elapsed)


