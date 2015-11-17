# -*- coding: utf-8 -*-
import unittest
import math

from util.point import Point
from util.util import limits, normalize_angle_2pi
from util.physic import MovableNewtonObject
from submarine.sub_turbines import Turbine


class Ship(MovableNewtonObject):
    def __init__(self, drag_factor, max_turn_per_hour, max_acceleration):
        super(Ship, self).__init__()
        self._rudder = 0
        self.max_turn_per_hour = max_turn_per_hour
        self.drag_factor = drag_factor
        self._ship_bearing = 0  # the angle of the ship in relation to north, in radians
        self.frontal_drag_factor = drag_factor
        self.drag_factor = drag_factor
        self.drag_force = Point(0, 0)
        self.turbine_acceleration = Point(0, 0)
        self.turbine = Turbine(self, max_acceleration)


    def get_rudder(self):
        return self._rudder

    def set_rudder(self, angle):
        angle = limits(angle, -self.max_turn_per_hour, self.max_turn_per_hour)
        self._rudder = angle

    rudder = property(get_rudder, set_rudder, "Rudder")  # in radians per hour

    def get_rubber_bearing(self):
        angle_deg = -1 * math.degrees(self.get_rudder())
        return (90 - angle_deg) % 360

    def rudder_right(self):
        self.rudder = self.max_turn_per_hour

    def rudder_left(self):
        self.rudder = -self.max_turn_per_hour

    def rudder_center(self):
        self.rudder = 0

    def drag_acceleration(self):
        return self.drag_force

    def rotate(self, angle):
        new_angle = self._ship_bearing + angle
        self._ship_bearing = normalize_angle_2pi(new_angle)

    def turn(self, time_elapsed):  # time in seconds
        self.turbine.turn(time_elapsed)
        total_turbine_acceleration = self.turbine.get_acceleration()  # scalar value

        turbine_acceleration_x = math.cos(self._ship_bearing) * total_turbine_acceleration
        turbine_acceleration_y = math.sin(self._ship_bearing) * total_turbine_acceleration
        self.turbine_acceleration = Point(turbine_acceleration_x, turbine_acceleration_y)

        # diff is the difference between the angle the sub is moving and the angle of the ship is bearing
        # meaning the ship the turning left or right
        diff = self.course - self.ship_bearing

        # correction if the drag factor since the sub is making a turn
        self.drag_factor =  self.frontal_drag_factor * (1+abs(500 * math.sin(diff)))

        # drag force
        total_drag =  self.drag_factor * (self.speed ** 2)
        vel_angle = self._velocity.angle
        drag_x = math.cos(vel_angle) * total_drag
        drag_y = math.sin(vel_angle) * total_drag
        self.drag_force = Point(drag_x, drag_y)

        self._acceleration = self.turbine_acceleration - self.drag_force

        if self.rudder != 0:
            self.rotate(-1.0 * self.rudder * time_elapsed * self.speed)

        super(Ship, self).turn(time_elapsed)


    def get_ship_bearing(self):
        return self._ship_bearing

    def _set_ship_bearing(self, angle):
        self._ship_bearing = normalize_angle_2pi(angle)

    ship_bearing = property(get_ship_bearing, _set_ship_bearing, "Ship Bearing")

    def get_ship_bearing_degrees(self):
        return self._ship_bearing.bearing


    def get_course(self):
        return self._velocity.angle
        # return self._velocity.angle

    # def set_course(self, angle):
    #     '''
    #     :param angle: new angle in radians
    #     :return: none
    #     '''
    #     angle = normalize_angle_2pi(angle)
    #     self._velocity.angle = angle
    #     self._acceleration.angle = self._velocity.angle  # assumes the rotation also changes the acceleration

    course = property(get_course, None, "Course")

    def get_bearing(self):
        return self._velocity.bearing

    bearing = property(get_bearing, None, "Bearing")


    def __str__(self):
        return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚) rudder:{rudder}".format(
            p=self._position,
            v=self._velocity,
            vt=self._velocity.angle,
            va=self._velocity.bearing,
            a=self._acceleration,
            at=self._acceleration.angle,
            aa=self._acceleration.bearing,
            rudder=self.rudder)

    def debug(self):
        return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚)".format(
            p=self._position,
            v=self._velocity,
            vt=self._velocity.angle,
            va=self._velocity.bearing,
            a=self._acceleration,
            at=self._acceleration.angle,
            aa=self._acceleration.bearing)


class TestUtil(unittest.TestCase):
    def test_mov_stopped(self):
        m1 = Ship()
        m1.turn(20)
        self.assertEqual(m1.position, Point(0, 0))


if __name__ == '__main__':
    unittest.main()