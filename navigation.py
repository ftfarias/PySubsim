# -*- coding: utf-8 -*-
import math
import Queue

from util.util import normalize_angle_2pi, limits
from util.physic import MovableNewtonObject


class Navigation(object):
    def __init__(self, movable, MAX_SPEED=30):
        assert isinstance(movable, MovableNewtonObject)
        self.module_name = "NAV"
        self.movable = movable
        self.destination = None
        self._speed = 0  # in knots
        self._course = 0  # in radians
        self.waypoints = Queue.Queue()
        self.MAX_SPEED = MAX_SPEED

    def all_stop(self):
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
        self._course = normalize_angle_2pi(new_course)

    course = property(get_course, _set_course, None, "gets or sets the desired course in radians")

    def get_actual_speed(self):
        return self.movable.get_speed()

    def get_actual_course(self):
        return self.movable.get_course()

    def add_waypoint(self, dest):
        if self.destination:
            self.waypoints.put(dest)
        else:
            self.set_destination(dest)

    def get_actual_pos(self):
        return self.movable.get_pos()

    def status(self):
        set_course = self.course.bearing
        actual_course = (self.get_actual_course())
        set_speed = self.speed
        actual_speed = self.get_actual_speed()
        rudder_str = math.degrees(self.movable.rudder/60)
        if self.destination:
            return "NAV: {f}, moving to {to}, course {c_a}˚(set:{c_s:.0f}˚), speed {s_a:.1f}(set:{s_s:.1f}) rudder:{rud:.0f}˚".format(
                f=self.get_actual_pos().format(), to=self.destination.format(),
                c_a=actual_course, c_s=set_course,
                s_a=actual_speed, s_s=set_speed,
                rud=rudder_str)
        else:
            return "NAV: {f}, course {c_a}˚(set:{c_s:.0f}˚), speed {s_a:.1f}(set:{s_s:.1f}) rudder:{rud:.0f}˚".format(
                f=self.get_actual_pos().format(),
                c_a=actual_course, c_s=set_course,
                s_a=actual_speed, s_s=set_speed, rud=rudder_str)
        #return "Stopped at {p}, course {c_a}(set:{c_s:.0f})".format(p=self.get_pos().format(), c_a=actual_course, c_s=set_course)

    def __str__(self):
        return self.status()

    def turn(self, time_elapsed):
        movable = self.movable

        if abs(self.get_actual_speed() - self.speed) < 0.01:
            movable.acceleration = 0
        elif self.get_actual_speed() > self.speed:
            movable.acceleration = -5 * 60
        else:
            movable.acceleration = 2 * 60

        if self.destination:
            current_pos = movable.get_pos()
            angle_to_destination = current_pos.angle_to(self.destination)
            #print("Angle to destination: {0}".format(abs_angle_to_bearing(angle_to_destination)))
            self.course = angle_to_destination
            angle_difference = angle_to_destination - self.get_actual_course()
            #print("Angle diff: {0}".format(math.degrees(abs(angle_difference))))

            # if angle > 180, invert, so 270 -> -90, 345 -> -15, etc
            if angle_difference > math.pi:
                angle_difference -= 2*math.pi

            movable.rudder = angle_difference*60 * 2

            dist_to_destination = current_pos.distance_to(self.destination)
            if dist_to_destination < 0.01:
                if isinstance(self, SubModule):
                    self.add_message("Destination arrived at "+str(self.destination))
                if not self.waypoints.empty():
                    self.destination = self.waypoints.get()
                    self.waypoints.task_done()
                else:
                    self.destination = None
                    self.speed = 0


