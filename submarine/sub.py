# -*- coding: utf-8 -*-
import math
import random

from ship import Ship
from sub_sonar import Sonar
from linear_scale import linear_scaler
from sound.sound import sum_of_decibels
from sub_module import SubModule
from sub_tma import TMA
from sub_navigation import Navigation
from sea_object import SeaObject
from sound.sound import Sound

class Submarine(Ship, SeaObject):
    MAX_TURN_RATE_HOUR = math.radians(120) * 60  # max 120 degrees per minute, 360 in 3 minutes
    MAX_DEEP_RATE_FEET = 1  # 1 foot per second
    MAX_SPEED = 36.0 # Knots or nautical mile per hour
    MAX_ACCELERATION = 2.0 * 3600 # max acceleraton 2 Knots / second
    DRAG_FACTOR =  1.0 * MAX_ACCELERATION / (MAX_SPEED**2)
    # DRAG_FACTOR = 0.000771604938272


    def __init__(self, sea):
        # turbines 35,000 hp (26 MW), 1 auxiliary motor 325 hp (242 kW)
        Ship.__init__(self, self.DRAG_FACTOR, self.MAX_TURN_RATE_HOUR, self.MAX_ACCELERATION)
        self.kind = '688'
        self.messages = []
        self.sea = sea
        self.max_hull_integrity = 100  # in "damage points"
        self.hull_integrity = self.max_hull_integrity
        self.damages = None
        self.actual_deep = 60  # feet
        self.set_deep = 60  # feet
        self.message_stop = False

        # build ship

        self.nav = Navigation(self)
        self.comm = Communication(self)
        self.tma = TMA(self)
        self.sonar = Sonar(self)
        self.weapon = Weapon(self)


    # "stop" means the turn just stop because requeres pilot atention
    def add_message(self, module, msg, stop=False):
        self.messages.append("{0}: {1}".format(module, msg))
        self.message_stop = self.message_stop or stop

    def get_messages(self):
        return self.messages, self.message_stop

    def is_cavitating(self):
        """
        Assumes the noise is proportional to speed

        Cavitation:

        Cavitation occurs when the propeller is spinning so fast water bubbles at
        the blades' edges. If you want to go faster, go deeper first. Water
        pressure at deeper depth reduces/eliminates cavitation.

        If you have the improved propeller upgrade, you can go about 25% faster
        without causing cavitation.

        Rule of thumb: number of feet down, divide by 10, subtract 1, is the
        fastest speed you can go without cavitation.

        For example, at 150 feet, you can go 14 knots without causing cavitation.
        150/10 = 15, 15-1 = 14.

        You can get the exact chart at the Marauders' website. (url's at the end of
          the document)

        # cavitation doesn't occur with spd < 7
        max_speed_for_deep = max((self.actual_deep / 10) - 1, 7)
        cavitating = max_speed_for_deep < self.speed

        if cavitating and not self.cavitation:
            self.add_message("SONAR", "COMM, SONAR: CAVITATING !!!", True)

        self.cavitation = cavitating

        :return: sound in in decibels

        """
        max_speed_for_deep = max((self.actual_deep / 10) - 1, 7)
        return max_speed_for_deep < self.speed

    def clear_messages(self):
        self.messages = []
        self.message_stop = False

    def all_stop(self):
        self.nav.all_stop()

    def periscope_deep(self):
        self.set_deep(60)

    # non-liner noise:
    # for 0 < speed < 15 :  linear from 40 to 60
    # for speed > 15 : linear with factor of 2db for each knot
    # ref: http://fas.org/man/dod-101/navy/docs/es310/uw_acous/uw_acous.htm
    NOISE_RANGE1 = linear_scaler([0, 15], [40, 60])
    NOISE_RANGE2 = linear_scaler([15, 35], [60, 100])

    # def self_noise(self, freq):  # returns
    #     # if self.speed <= 15:
    #     #     noise = self.NOISE_RANGE1(self.speed)
    #     # else:
    #     #     noise = self.NOISE_RANGE2(self.speed)
    #
    #     # cavitation doesn't occur with spd < 7
    #     # max_speed_for_deep = max((self.actual_deep / 10) - 1, 7)
    #     # cavitating = max_speed_for_deep < self.speed
    #
    #     return noise + (30 if self.cavitation else 0) + random.gauss(0, 0.4)
    #
    #     '''
    #     Above 10-20 kts, flow noise becomes the dominant factor and significantly increases
    #     with speed (@1.5-2 dB/KT)
    #     '''
    #
    #
    #     return noise + (30 if cavitating else 0) + random.gauss(0, 0.4)


    def get_self_noise(self, freq):  # returns
        """
        """
        s = Sound()

        s.logdecay(120,30,100,300)  # 120db @ 30Hz - 100db @ 300 db

        return s

        # if self.speed <= 15:
        #     noise = self.NOISE_RANGE1(self.speed)
        # else:
        #     noise = self.NOISE_RANGE2(self.speed)


        # logfreq = math.log10(freq)
        # if self.is_cavitating():
        #     base = [0]
        # else:
        #     base = [150]
        #
        #
        # if freq <= 100:
        #     base.append(noise)
        #
        # if freq > 100:
        #     base.append(noise - 20 * math.log10(freq/100))

        # return sum_of_decibels(base) + random.gauss(0, 1)

    def turn(self, time_elapsed):

        Ship.turn(self, time_elapsed)

        # self.speed = self.speed - ( self.drag_acceleration() * time_elapsed)

        # deep
        deep_diff = self.set_deep - self.actual_deep
        if abs(deep_diff) > 0.1:
            dive_rate = min(deep_diff, self.MAX_DEEP_RATE_FEET)
            self.actual_deep += dive_rate * time_elapsed * 3600



        self.nav.turn(time_elapsed)
        self.comm.turn(time_elapsed)
        self.sonar.turn(time_elapsed)
        self.tma.turn(time_elapsed)
        self.weapon.turn(time_elapsed)

    def __str__(self):
        return "Submarine: {status}  deep:{deep:.0f}({sdeep})".format(status='',
                                                                      deep=self.actual_deep, sdeep=self.set_deep)





class Weapon(SubModule):
    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "WEAPON"


class Torpedo():
    pass


class Communication(SubModule):
    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "COMM"


"""
- http://www.naval-technology.com/projects/nssn/
- http://www.naval-technology.com/projects/la/
- https://actuv.darpa.mil/
- http://www.subsim.com/radioroom
- http://manglermuldoon.blogspot.com.br/2013_12_01_archive.html
- http://www.subsim.com/radioroom/showthread.php?t=214023


the 093’s noise level has been reduced to that of
the Russian Akula-class submarine at 110 decibels.
He states that the 094’s acoustic signature has been
reduced to 120 decibels. According to this report,
this is definitely not equal to that of the Ohio class,
but is on a par with the Los Angeles. There is no additional
information given to evaluate concerning the origins or
comparability of these 'data.'" - Andrew S. Erickson & Lyle J. Goldstein, 2006.

As a reminder, a decibel is: "a unit used to measure the intensity
of a sound or the power level of an electrical signal by comparing
it with a given level on a logarithmic scale" - American English in
Oxford dictionary, 2013.

Decibels do not scale linearly. A 3db change is signifies a
doubling power and a change of 10 db signifies the power increasing
by a factor of ten.  Therefore, the 636 Kilo class with an acoustic
signature of 105 decibels is 10 times as loud as the 95 decibel
acoustic signature of the Virginia class submarine.

To provide a point of reference, the following acoustic
signatures are from "Chinese Evaluations of the U.S. Navy Submarine Force"
 and "CHINA’S FUTURE NUCLEAR SUBMARINE FORCE"

Ocean background noise - 90 decibels
Seawolf-class - 95 decibels
Virginia-class - 95 decibels
636 Kilo class - 105 decibels
Akula-class - 110 decibels
Type 093 - 110 decibels
Type 094 - 120 decibels

The Shang has an acoustic signature similar to the original
Russian Akula class boats or roughly equivalent to the original
Los-Angles class submarine, not the 688I (improved Los-Angles class).
Judging from acoustic signatures, the most modern Chinese nuclear
submarines are comparabile to 1970s and 1980s US and Soviet
designs shown on the chart below.




DEEP:

During World War II, American fleet submarines normally operated at a depth of 200 feet,
 though in emergencies they would dive to a depth of 400 feet.

Post-War American submarines, both conventional and nuclear, had improved designs
and were constructed of improved materials [the equivalent of "HY-42"]. These boats
 had normal operating depths of some 700 feet, and a crush depth of 1100 feet.

The Thresher, the first American submarine constructed of HY-80 steel, reportedly
 had a normal operating depth of 1,300 feet, roughly two-thirds the crush depth limit
  imposed by the HY-80 steel.

The Seawolf, the first American submarine constructed of HY-100 steel, is officially
claimed by the Navy to have a normal operating depth of "greater than 800 feet," but based
on the reported operating depth of the Thresher, it may be assumed that the normaly operating
 depth of the Seawolf is roughly double the official figure.

The Soviet Alfa submarines, constructed of titanium, reportedly had an operating depth
of nearly 4,000 feet.
"""
