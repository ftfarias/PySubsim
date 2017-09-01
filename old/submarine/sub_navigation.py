# -*- coding: utf-8 -*-
import math
import Queue

from sub_module import SubModule
from util.util import angle_to_bearing, normalize_angle_2pi, limits
from util.point import Point


class Navigation(SubModule):
    def __init__(self, sub):
        self.module_name = "NAV"
        self.sub = sub
        self._destination = None
        self._speed = None
        self._course = 0
        self.waypoints = Queue.Queue()
        self.acceleration_needed = 0
        self.turbine_level_needed = 0
        self.angle_to_destination = 0
        self.angle_difference = 0

    def get_active(self):
        return (self.destination != None)

    def set_manual(self):
        self._destination = None

    def stop_all(self):
        self.set_speed(0)

    def get_destination(self):
        return self._destination

    def set_destination(self, destination):
        assert isinstance(destination, Point)
        self._destination = destination

    destination = property(get_destination, set_destination, None, "destination")

    def get_speed(self):
        return self._speed

    def _set_speed(self, new_speed):
        self._speed = new_speed


    speed = property(get_speed, _set_speed, None, "gets or sets the desired speed in knots")

    # def get_course(self):
    #     return self._course
    #
    # def _set_course(self, new_course):
    #     self._course = normalize_angle_2pi(new_course)
    #
    # course = property(get_course, _set_course, None, "gets or sets the desired course in radians")

    def add_waypoint(self, dest):
        if self.destination:
            self.waypoints.put(dest)
        else:
            self.set_destination(dest)

    def status(self):
        return ""
        # set_course = angle_to_bearing(self.course)
        # actual_course = angle_to_bearing(self.get_actual_course())
        # set_speed = self.speed
        # actual_speed = self.get_actual_speed()
        # rudder_str = math.degrees(self.sub.rudder/60)
        # if self.destination:
        #     return "NAV: {f}, moving to {to}, course {c_a}˚(set:{c_s:.0f}˚), speed {s_a:.1f}(set:{s_s:.1f}) rudder:{rud:.0f}˚".format(
        #         f=self.get_pos().format(), to=self.destination.format(),
        #         c_a=actual_course, c_s=set_course,
        #         s_a=actual_speed, s_s=set_speed,
        #         rud=rudder_str)
        # else:
        #     return "NAV: {f}, course {c_a}˚(set:{c_s:.0f}˚), speed {s_a:.1f}(set:{s_s:.1f}) rudder:{rud:.0f}˚".format(
        #         f=self.get_pos().format(),
        #         c_a=actual_course, c_s=set_course,
        #         s_a=actual_speed, s_s=set_speed, rud=rudder_str)
        #return "Stopped at {p}, course {c_a}(set:{c_s:.0f})".format(p=self.get_pos().format(), c_a=actual_course, c_s=set_course)

    def __str__(self):
        return self.status()

    def turn(self, time_elapsed):
        sub = self.sub
        current_speed = sub.speed
        set_speed = self.speed
        if set_speed is not None:
            self.acceleration_needed = sub.drag_factor * (set_speed**2)
            self.turbine_level_needed = 100.0 * self.acceleration_needed / sub.turbine.max_acceleration
            # adjust turbines
            diff = self.speed - sub.speed
            diff_turbine = sub.turbine.level - self.turbine_level_needed
            sub.turbine.level  = self.turbine_level_needed + (diff * 10)

            # if diff > 5:
            #     sub.turbine.increase(2)
            # elif diff > 0:
            #     if diff_turbine > 10:
            #         sub.turbine.increase(1)
            #     else:
            #         sub.turbine.decrease(1)
            #
            #     # sub.turbine.level = min(self.turbine_level_needed + (diff * (100 - self.turbine_level_needed)), 50)
            #     # sub.turbine.increase(0)
            # elif diff < -5:
            #     sub.turbine.decrease(1)
            # elif diff < 0:
            #     if diff_turbine > 0:
            #         sub.turbine.increase(1)
            #     else:
            #         sub.turbine.decrease(1)
                # sub.turbine.level = max(self.turbine_level_needed + (diff * (100 - self.turbine_level_needed)), -20)
                # sub.turbine.decrease(2)

        if self.destination:
            self.angle_to_destination = sub.position.angle_to(self.destination)
            # self.angle_difference = self.angle_to_destination - sub.ship_bearing
            self.angle_difference = self.angle_to_destination - sub.course
            #print("Angle diff: {0}".format(math.degrees(abs(angle_difference))))

            # if angle > 180, invert, so 270 -> -90, 345 -> -15, etc
            # if self.angle_difference > math.pi:
            #     self.angle_difference -= 2*math.pi

            sub.rudder = self.angle_difference * -30.0





        #
        # if abs(self.get_actual_speed() - self.speed) < 0.01:
        #     sub.acceleration = 0
        # elif self.get_actual_speed() > self.speed:
        #     sub.acceleration = -5 * 60
        # else:
        #     sub.acceleration = 2 * 60
        #


            # dist_to_destination = current_pos.distance_to(self.destination)
            # if dist_to_destination < 0.01:
            #     self.add_message("Destination arrived at "+str(self.destination))
            #     if not self.waypoints.empty():
            #         self.destination = self.waypoints.get()
            #         self.waypoints.task_done()
            #     else:
            #         self.destination = None
            #         self.speed = 0
