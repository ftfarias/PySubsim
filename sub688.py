# -*- coding: utf-8 -*-
import math

from util.point import Point
from util.util import limits, normalize_angle_2pi, normalize_angle_pi
from util.linear_scale import linear_scaler

class Submarine688(object):
    MAX_TURN_RATE_HOUR = math.radians(120) * 60  # max 120 degrees per minute, 360 in 3 minutes
    MAX_DEEP_RATE_FEET = 1  # 1 foot per second
    MAX_SPEED = 36.0  # Knots or nautical mile per hour
    MAX_ACCELERATION = 1.0 * 3600 # acceleration in knots/hour^2 -> max acceleration 0.1 Knots / second^2
    DRAG_FACTOR = 1.0 * MAX_ACCELERATION / (MAX_SPEED ** 2)

    NAV_MODE_MANUAL = 'manual'
    NAV_MODE_DESTINATION = 'destination'

    def __init__(self):
        # turbines 35,000 hp (26 MW), 1 auxiliary motor 325 hp (242 kW)
        # Ship.__init__(self, self.DRAG_FACTOR, self.MAX_TURN_RATE_HOUR, self.MAX_ACCELERATION)

        self.kind = '688'
        self.messages = []
        self.max_hull_integrity = 100  # in "damage points"
        self.hull_integrity = self.max_hull_integrity
        self.damages = None
        self._actual_deep = 60  # feet
        self._target_deep = 60  # feet

        ### Physics ###
        self._position = Point(0, 0)
        self._velocity = Point(0, 0)
        self._acceleration = Point(0, 0)

        self._target_speed = 0
        self._rudder = 0  # property rudder in radians pe minute
        self._ship_course = 0  # the angle of the ship in radians
        self._turbine_level = 0  # 0 to 100%

        self.total_drag_acceleration = 0
        self.drag_acceleration = Point(0, 0)
        self.acceleration_needed = 0
        self.turbine_level_needed = 0

        self.turbine_acceleration = 0
        self.turbine_acceleration_x = 0
        self.turbine_acceleration_y = 0
        self.time_elapsed = 0

        self.nav_mode = self.NAV_MODE_MANUAL
        self._destination = Point(0,0)

    ### TURBINE ###

    def get_turbine_level(self):
        return self._turbine_level

    def set_turbine_level(self, new_level):
        self._turbine_level = limits(new_level, -100, 100)

    turbine_level = property(get_turbine_level, set_turbine_level, None, "level of power in the turbine (-100% to +100%)")

    ### DEEP ###

    def get_actual_deep(self):
        return self._actual_deep;

    actual_deep = property(get_actual_deep, None, None, "Target Deep")


    def set_periscope_deep(self):
        self.target_deep = 60

    def get_target_deep(self):
        return self._target_deep

    def set_target_deep(self, value):
        self._target_deep = limits(value, 0, 9000)

    target_deep = property(get_target_deep, set_target_deep, None, "Target Deep")

    ### Position ###

    def _get_position(self):
        return self._position

    def _set_position(self, value):
        self._position = value

    position = property(_get_position, _set_position, None, "Position")


    ### Speed ###
    def get_target_speed(self):
        return self._target_speed

    def set_target_speed(self, value):
        self._target_speed = limits(value, 0, self.MAX_SPEED)

    target_speed = property(get_target_speed, set_target_speed, None, "Target Speed")

    def get_actual_speed(self):
        return self._velocity.length

    def _set_actual_speed(self, value):
        self._velocity.length = limits(value, 0, self.MAX_SPEED)

    actual_speed = property(get_actual_speed, None, None, "Actual Speed")

    def all_stop(self):
        self.set_target_speed(0)

    ### Acceleration ###

    def _get_acceleration(self):
        return self._acceleration.length

    def _set_acceleration(self, value):
        self._acceleration.length = value

    acceleration = property(_get_acceleration, _set_acceleration, None, "Acceleration")

    ### Drag ###

    def get_drag_acceleration(self):
        return self.drag_force

    ### NAVIGATION ###

    def get_rubber_bearing(self):
        angle_deg = -1 * math.degrees(self.get_rudder())
        return (90 - angle_deg) % 360

    def rudder_right(self):
        self.rudder = self.MAX_TURN_RATE_HOUR

    def rudder_left(self):
        self.rudder = -self.MAX_TURN_RATE_HOUR

    def rudder_center(self):
        self.rudder = 0

    def get_rudder(self):
        return self._rudder

    def set_rudder(self, angle):
        angle = limits(angle, -self.MAX_TURN_RATE_HOUR, self.MAX_TURN_RATE_HOUR)
        self._rudder = angle

    rudder = property(get_rudder, set_rudder, "Rudder")  # in radians per hour

    def get_ship_course(self):
        return self._velocity.get_angle()

    def _set_ship_course(self, angle):
        self._ship_course = normalize_angle_2pi(angle)

    course = property(get_ship_course, _set_ship_course, "Ship Course")

    def get_destination(self):
        return self._destination

    def set_destination(self, destination):
        self._destination = destination
        self.nav_mode = self.NAV_MODE_DESTINATION

    destination = property(get_destination, set_destination, "Ship Destination")


    ### Message ###

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
        return max_speed_for_deep < self.actual_speed

    def clear_messages(self):
        self.messages = []
        self.message_stop = False

    # non-liner noise:
    # for 0 < speed < 15 :  linear from 40 to 60
    # for speed > 15 : linear with factor of 2db for each knot
    # ref: http://fas.org/man/dod-101/navy/docs/es310/uw_acous/uw_acous.htm
    NOISE_RANGE1 = linear_scaler([0, 15], [40, 60])
    NOISE_RANGE2 = linear_scaler([15, 35], [60, 100])

    # def self_noise(self, freq):  # returns
    # # if self.speed <= 15:
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

    ACUSTIC_PROFILE = {
        2: 112.0,
        4: 108.0,
        5: 115.0,
        8: 110.0
    }

    def get_self_noise(self):  # returns
        """
        """
        # s = Sound()
        #
        # s.add_frequencs(self.ACUSTIC_PROFILE)
        #
        # base_sound_level = 100  # db - "Very quite submarine"
        # s.add_logdecay(base_sound_level, 1, base_sound_level, 100)
        # s.add_logdecay(base_sound_level, 100, base_sound_level - 20, 1000)
        #
        #
        # # machine noise
        # # 5 - 400Hz, proportional to turbine level
        # turbine_noise = 75 + math.log10((abs(self.turbine.get_level())+0.01)) * 40
        #
        # s.add_logdecay(turbine_noise, 1, turbine_noise - 10, 400)
        #
        # # flow noise
        # flow_nose = (abs(self.get_speed()) * 6.0)
        #
        # # s.add_logdecay(noise_30hz,5,noise_30hz,30)  # 120db @ 30Hz - 100db @ 300 db
        # s.add_logdecay(flow_nose, 100, flow_nose-20, 1000)  # 120db @ 30Hz - 100db @ 300 db
        #
        # return s.add_noise(0.5)
        return 100


    # def get_sea_noise(self):  # returns
    #     return self.sea.get_sea_noise(self.actual_deep)

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
        self.time_elapsed = time_elapsed
        # change speed if necessary
        if self.actual_speed !=  self.target_speed:
            self.acceleration_needed = self.DRAG_FACTOR * (self.target_speed**2)
            self.turbine_level_needed = 100.0 * self.acceleration_needed / self.MAX_ACCELERATION

            # adjust turbines
            diff_speed = self.target_speed - self.actual_speed
            diff_turbine = self.turbine_level - self.turbine_level_needed
            # diff*10 gives more burst to make the change in speed faster
            self.turbine_level  = self.turbine_level_needed  + (diff_speed * 5)

        # ship_moviment_angle is the angle the ship is moving
        ship_moviment_angle = self._velocity.get_angle()

        # ship_rotation_angle is the angle the ship pointing
        ship_course_angle = self._ship_course

        # drifting_angle_diff is the difference between the angle the sub is moving and the angle of the ship is bearing
        # meaning the ship the turning left or right
        drifting_angle_diff = normalize_angle_2pi(ship_moviment_angle - ship_course_angle)

        self.turbine_acceleration = self.MAX_ACCELERATION * self.turbine_level / 100
        self.turbine_acceleration_x = math.cos(ship_course_angle) * self.turbine_acceleration
        self.turbine_acceleration_y = math.sin(ship_course_angle) * self.turbine_acceleration
        self.turbine_acceleration = Point(self.turbine_acceleration_x, self.turbine_acceleration_y)

        if self.rudder != 0:
            # rotate the ship
            angle_to_rotate = self.rudder * time_elapsed  * (self.actual_speed / 3)
            new_angle = ship_course_angle + angle_to_rotate
            self._ship_course = normalize_angle_pi(new_angle)

        # correction if the drag factor since the sub is making a turn
        self.drag_factor = self.DRAG_FACTOR * (1 + abs(500 * math.sin(drifting_angle_diff)))

        # drag force
        self.total_drag_acceleration = -1.0 * self.drag_factor * ((self.actual_speed) ** 2)
        drag_x = math.cos(ship_moviment_angle) * self.total_drag_acceleration
        drag_y = math.sin(ship_moviment_angle) * self.total_drag_acceleration
        self.drag_acceleration = Point(drag_x, drag_y)

        self._acceleration = self.turbine_acceleration + self.drag_acceleration # convert seconds to hours
        self._velocity += self._acceleration * time_elapsed
        self._position += self._velocity * time_elapsed

        # deep
        deep_diff = self.target_deep - self.actual_deep
        if abs(deep_diff) > 0.1:
            dive_rate = min(deep_diff, self.MAX_DEEP_RATE_FEET)
            self.actual_deep += dive_rate * time_elapsed * 3600


        if self.nav_mode == self.NAV_MODE_DESTINATION:
            self.angle_to_destination = self.position.get_angle_to(self.destination)
            # self.angle_difference = self.angle_to_destination - sub.ship_bearing
            self.angle_difference = normalize_angle_pi(self.angle_to_destination - self.course)
            #print("Angle diff: {0}".format(math.degrees(abs(angle_difference))))

            # if angle > 180, invert, so 270 -> -90, 345 -> -15, etc
            # if self.angle_difference > math.pi:
            #     self.angle_difference -= 2*math.pi

            self.rudder = self.angle_difference * -30.0


    def __str__(self):
        return "Sub: {status}  deep:{deep:.0f}({sdeep})".format(status='',
                                                                      deep=self.actual_deep, sdeep=self.target_deep)



        # def __str__(self):
    #     return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚)".format(
    #         p=self._position,
    #         v=self._velocity,
    #         vt=self._velocity.angle,
    #         va=self._velocity.bearing,
    #         a=self._acceleration,
    #         at=self._acceleration.angle,
    #         aa=self._acceleration.bearing)


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

import unittest


class TestUtil(unittest.TestCase):
    def test_mov_stopped(self):
        m1 = Submarine688()
        m1.turn(20)
        self.assertEqual(m1.position, Point(0, 0))

    def test_mov_stopped(self):
        m1 = Submarine688()
        m1.turn(20)
        self.assertEqual(m1.position, Point(0, 0))

    def test_mov_vel_contant(self):
        m1 = Submarine688()
        m1._velocity = Point(1, 2)
        m1.turn(20)
        self.assertAlmostEqual(m1.position.x, 20)
        self.assertAlmostEqual(m1.position.y, 40)

    def test_mov_vel_contant2(self):
        m1 = Submarine688()
        m1._velocity = Point(1, 2)
        m1.turn(10)
        self.assertAlmostEqual(m1.position.x, 10)
        self.assertAlmostEqual(m1.position.y, 20)
        m1.turn(5)
        m1.turn(5)
        self.assertAlmostEqual(m1.position.x, 20)
        self.assertAlmostEqual(m1.position.y, 40)

    def test_mov_speed(self):
        m1 = Submarine688()
        m1._velocity = Point(4, 3)
        self.assertEqual(m1.speed, 5)

    def test_mov_speed2(self):
        m1 = Submarine688()
        m1._velocity = Point(3, -4)
        self.assertEqual(m1.speed, 5)

    def test_mov_speed3(self):
        m1 = Submarine688()
        m1._velocity = Point(6, 8)
        self.assertEqual(m1.speed, 10)


if __name__ == '__main__':
    unittest.main()