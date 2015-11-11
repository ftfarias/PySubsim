# -*- coding: utf-8 -*-
from sub_module import SubModule
from util import abs_angle_to_bearing, normalize_angle360, limits
import math
import Queue

class Navigation(SubModule):
    def __init__(self, sub, MAX_SPEED=30):
        self.module_name = "NAV"
        self.sub = sub
        self.destination = None
        self._speed = 0
        self._course = 0
        self.waypoints = Queue.Queue()
        self.MAX_SPEED = MAX_SPEED


    def set_manual(self):
        self.destination = None

    def stop_all(self):
        self.set_speed(0)

    def set_destination(self, destination):
        self.destination = destination

    def get_speed(self):
        return self._speed

    def _set_speed(self, new_speed):
        self._speed = limits(new_speed, 0, self.MAX_SPEED)

    speed = property(get_speed, _set_speed, None, "gets or sets the desired speed")

    def get_course(self):
        return self._course

    def _set_course(self, new_course):
        self._course = normalize_angle360(new_course)

    course = property(get_course, _set_course, None, "gets or sets the desired course")

    def get_actual_speed(self):
        return self.sub.get_speed()

    def get_actual_course(self):
        return self.sub.get_course()

    def add_waypoint(self, dest):
        if self.destination:
            self.waypoints.put(dest)
        else:
            self.set_destination(dest)

    def get_pos(self):
        return self.sub.get_pos()

    def status(self):
        set_course = abs_angle_to_bearing(self.course)
        actual_course = abs_angle_to_bearing(self.get_actual_course())
        set_speed = self.speed
        actual_speed = self.get_actual_speed()
        rudder_str = math.degrees(self.sub.rudder/60)
        if self.destination:
            return "NAV: {f}, moving to {to}, course {c_a}˚(set:{c_s:.0f}˚), speed {s_a:.1f}(set:{s_s:.1f}) rudder:{rud:.0f}˚".format(
                f=self.get_pos().format(), to=self.destination.format(),
                c_a=actual_course, c_s=set_course,
                s_a=actual_speed, s_s=set_speed,
                rud=rudder_str)
        else:
            return "NAV: {f}, course {c_a}˚(set:{c_s:.0f}˚), speed {s_a:.1f}(set:{s_s:.1f}) rudder:{rud:.0f}˚".format(
                f=self.get_pos().format(),
                c_a=actual_course, c_s=set_course,
                s_a=actual_speed, s_s=set_speed, rud=rudder_str)
        #return "Stopped at {p}, course {c_a}(set:{c_s:.0f})".format(p=self.get_pos().format(), c_a=actual_course, c_s=set_course)

    def __str__(self):
        return self.status()

    def turn(self, time_elapsed):
        sub = self.sub

        if abs(self.get_actual_speed() - self.speed) < 0.01:
            sub.acceleration = 0
        elif self.get_actual_speed() > self.speed:
            sub.acceleration = -5 * 60
        else:
            sub.acceleration = 2 * 60

        if self.destination:
            current_pos = sub.get_pos()
            angle_to_destination = current_pos.angle_to(self.destination)
            #print("Angle to destination: {0}".format(abs_angle_to_bearing(angle_to_destination)))
            self.sub.set_sub_rudder(angle_to_destination)
            self.course = angle_to_destination
            angle_difference = angle_to_destination - self.get_actual_course()
            #print("Angle diff: {0}".format(math.degrees(abs(angle_difference))))

            # if angle > 180, invert, so 270 -> -90, 345 -> -15, etc
            if angle_difference > math.pi:
                angle_difference -= 2*math.pi

            sub.set_sub_rudder(angle_difference*60 * 2)

            # dist_to_destination = current_pos.distance_to(self.destination)
            # if dist_to_destination < 0.01:
            #     self.add_message("Destination arrived at "+str(self.destination))
            #     if not self.waypoints.empty():
            #         self.destination = self.waypoints.get()
            #         self.waypoints.task_done()
            #     else:
            #         self.destination = None
            #         self.speed = 0
