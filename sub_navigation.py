from sub_module import SubModule
from util import abs_angle_to_bearing, normalize_angle
import math

class Navigation(SubModule):
    MAX_SPEED = 30

    def __init__(self, sub):
        self.module_name = "NAV"
        self.sub = sub
        self.destination = None
        self._speed = 0
        self._course = 0
        self.waypoints = []

    def stop_all(self):
        self.set_speed(0)

    def set_destination(self, destination):
        self.destination = destination

    def get_speed(self):
        return self._speed

    def __set_speed(self, new_speed):
        self._speed = min(new_speed, self.MAX_SPEED)

    speed = property(get_speed, __set_speed, None, "gets or sets the desired speed")

    def get_course(self):
        return self._course

    def __set_course(self, new_course):
        self._course = normalize_angle(new_course)

    course = property(get_course, __set_course, None, "gets or sets the desired course")

    def get_actual_speed(self):
        return self.sub.vel.lenght

    def get_actual_course(self):
        return self.sub.get_course()

    def add_waypoint(self, dest):
        self.waypoints.append(dest)

    def get_pos(self):
        return self.sub.get_pos()

    def status(self):
        set_course = abs_angle_to_bearing(self.course)
        actual_course = abs_angle_to_bearing(self.get_actual_course())
        if self.destination:
            return "Moving from {f} to {to}, course {c_a}(set:{c_s:.0f}), speed {s}".format(
                f=self.get_pos().format(), to=self.destination.format(), s=self.speed, c_a=actual_course, c_s=set_course)
        else:
            return "Stopped at {p}, course {c_a}(set:{c_s:.0f})".format(p=self.get_pos().format(), c_a=actual_course, c_s=set_course)

    def turn(self, time_elapsed):
        if self.destination:
            current_pos = self.sub.pos
            angle_to_destiny = current_pos.angle_to(self.destination)
            self.sub.set_sub_rudder(angle_to_destiny)

            dist_to_move = self.speed * time_elapsed
            dist_to_destination = self.pos.distance_to(self.destination)
            if dist_to_destination > 0:
                dist = min(dist_to_move,dist_to_destination)
                self.pos = self.pos + (self.pos.movement_to(self.destination) * dist)
            else:
                self.add_message("destination arrived at "+str(self.destination))
                self.destination = None
                self.speed = 0
