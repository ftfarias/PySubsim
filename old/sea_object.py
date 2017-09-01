# -*- coding: utf-8 -*-
import random
import math

from util.util import Bands
from util.physic import Point, MovableNewtonObject
from navigation import Navigation
from sound.sound import Sound

"""
SS
Conventional
attack
submarine
SSN
Nuclear - powered
attack
submarine
SSB
Conventional
ballistic
missile
submarine
SSBN
Nuclear - powered
ballistic
missile
submarine
SSG
Conventional
guided
missile
submarine
SSGN
Nuclear - powered
guided
missile
submarine
"""
class SeaObject(object):
    def __init__(self, sea):
        self.id = None
        self.sound = Sound()
        self.pos = Point(0, 0)
        self.sea = sea
        self.deep = 0

    def turn(self, time_elapsed):
        pass

    def get_id(self):
        return self.id

    def get_sound(self):
        return self.sound

    def get_pos(self):
        return self.pos

    def get_deep(self):
        return self.deep;

    # def get_broadband(self):
    #     return self.sound.total_decibels()
    #
    # def get_narrowband(self):
    #     return self.sound.get_bands()

    def __str__(self):
        #return self.kind
        return "pos:{pos} deep={deep}".format(
            deep=self.get_deep(), pos=self.get_pos())


class SnappingShrimp(SeaObject):
    # "The snapping shrimp competes with much larger animals
    # such as the Sperm Whale and Beluga Whale for the title of
    # 'loudest animal in the sea'. The animal snaps a specialized claw
    # shut to create a cavitation bubble that generates acoustic pressures
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

    # Snapping shrimp inhabit shallow tropical and semi-tropical waters having
    # a bottom of rock, shell, or weed that offers the animals some concealment.
    # Colonies of snapping shrimp generate sounds with broad spectral peaks at
    # frequencies of 2-5 kHz. Individual snaps can have peak-to-peak
    # source levels as high as 189 underwater dB at 1 m.
    # Sound generated by colonies of snapping shrimp can dominate
    # other sources of background noise in shallow tropical waters.
    # http://www.dosits.org/science/soundsinthesea/commonsounds/

    def __init__(self, sea):
        SeaObject.__init__(self, sea)
        self.snapping = False
        self.counter = random.randint(3, 20) + random.gauss(5, 10)
        # generate intense broadband noise, f = 1-10 kHz, SL = 60-90 dB
        # bands: 5 to 10 high frequence bands
        self.bands = Bands().add_random([1000, 10000], [100, 120], times=random.randint(5, 10))
        self.deep = random.randint(9, 20)

    def turn(self, time_elapsed):
        self.counter -= time_elapsed
        if self.snapping:
            if self.counter <= 0:
                # Stop snapping
                self.snapping = False
                self.counter = random.randint(1, 10) + random.randint(1, 10) + random.randint(1, 10)
        else:
            # in silence
            if self.counter <= 0:
                # Stars to snapping
                self.snapping = True
                self.counter = random.gauss(8, 5) + random.gauss(12, 5)

    def get_bands(self):
        if self.snapping:
            return self.bands
        else:
            return Bands()  # Silence

class Buoy(SeaObject):
    def __init__(self, sea, pos, sound, deep=0):
        SeaObject.__init__(self, sea)
        self.sound = sound
        self.pos = pos
        self.deep = deep

class SonarBuoy(SeaObject):
    def __init__(self, sea, pos, freq, db, deep=0):
        SeaObject.__init__(self, sea)
        s = Sound()
        s.set_frequency(freq,db)
        self.sound = s
        self.pos = pos
        self.deep = deep

class MovableSeaObject(SeaObject, MovableNewtonObject):
    def __init__(self, sea, max_speed = 40, max_turn_rate_hour = math.radians(360)*60):  # max 360 degrees per minute
        SeaObject.__init__(self, sea)
        MovableNewtonObject.__init__(self, max_speed, max_turn_rate_hour)

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):
        MovableNewtonObject.turn(self, time_elapsed)

        # def set_destination(self, course, speed):
        # self.vel = Point(1,1)  # just to initialize the vector
        #     self.speed = speed
        #     self.course = course

    def __str__(self):
        return MovableNewtonObject.__str__(self)


class Whale(MovableSeaObject):
    # f = 12 Hz - @2-5 kHz for “whale songs”, SL up to 188 dB
    # Swimming: 10 - 20 Hz, 60 to 80 DB
    # Sing: 2Khz - 5 Khz, 120 to 190 DB (AI should handle this later)
    def __init__(self, sea):
        MovableSeaObject.__init__(self, sea, 15)
        self.nav = Navigation(self)
        self.sea = sea
        self.nav.destination = None
        self.bands_swim = Bands().add_random([10, 20], [60, 80])
        self.bands_swim_sing = self.bands_swim.add_random([2000, 5000], [120, 150], times=3)
        self.deep = random.randint(10, 20)
        print ("Swim: " + str(self.bands_swim))
        print ("Sing: " + str(self.bands_swim_sing))
        self.singing = False
        self.counter = (random.randint(5, 10) + random.gauss(6, 5)) / 60

        # The blue whale is a marine mammal belonging to the suborder of
        # baleen whales (called Mysticeti). At up to 32.9 metres (108 ft)
        # in length and 172 metric tons (190 short tons) or more in weight,
        # it is the largest animal ever to have existed.
        #
        # Blue whales can reach speeds of 50 kilometres per hour (31 mph)
        # over short bursts, usually when interacting with other whales, but 20
        # kilometres per hour (12 mph) is a more typical traveling speed. When feeding,
        # they slow down to 5 kilometres per hour (3.1 mph).

    def turn(self, time_elapsed):
        MovableSeaObject.turn(self, time_elapsed)
        self.nav.turn(time_elapsed)
        self.counter -= time_elapsed
        if self.counter <= 0:
            if self.singing:
                self.singing = False
                self.counter = (random.randint(10, 5) + random.gauss(5, 5)) / 60
            else:
                self.singing = True
                self.counter = (random.gauss(10, 3) + 5) / 60

        if self.nav.destination is None:
            self.nav.destination = Point(random.randint(0, 10), random.randint(0, 10))
            self.nav.speed = (random.random() * 10) + 3

    def get_deep(self):
        return self.deep

    def get_pos(self):
        return self.pos

    def get_bands(self):
        if self.singing:
            return self.bands_swim_sing
        else:
            return self.bands_swim

    def __str__(self):
        return "Whale {is_singing}, {pos}, swim:{swim}, sing:{sing}, counter:{counter}, dest:{dest}".format(
                                                                               is_singing = self.singing,
                                                                               pos=MovableSeaObject.__str__(self),
                                                                               swim=str(self.bands_swim),
                                                                               sing=str(self.bands_swim_sing),
                                                                               counter=self.counter,
                                                                               dest=self.nav.destination)


class Ship(MovableSeaObject):
    def __init__(self, sea):
        MovableSeaObject.__init__(self, sea)
        self.navigation = Navigation(self)

    def get_deep(self):
        return 0

    def get_pos(self):
        return self.pos

    def turn(self, time_elapsed):
        MovableSeaObject.turn(self, time_elapsed)

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
        MovableSeaObject.turn(self, time_elapsed)




class Torpedo(MovableSeaObject):
    def __init__(self, sea):
        MovableSeaObject.__init__(self, sea, max_speed=42, max_turn_rate_hour=math.radians(720)*60)
        self.navigation = Navigation(self)
        self.deep = 100
        self.armed = False
        self.fuel = 100 * 40 # seconds at 40 knots

    def launch(self, pos, speed = 40):
        self.navigation.set_destination(pos)
        self.speed = speed

    def get_deep(self):
        return self.deep

    def get_fuel_consumption(self, time_elapsed):
        # 1 fuel unit per second per knot
        return 1.0 * time_elapsed * self.navigation.get_actual_speed()

    def turn(self, time_elapsed):
        MovableSeaObject.turn(self, time_elapsed)
        self.fuel -= self.get_fuel_consumption(time_elapsed)
        if self.fuel <= 0:
            self.navigation.MAX_SPEED = 0
            self.MAX_SPEED = 0

    def explode(self):
        self.sea.report_explosion(self.get_pos())