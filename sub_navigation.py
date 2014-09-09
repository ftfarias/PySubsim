from sub_module import SubModule
from util import abs_angle_to_bearing
import math

class Navigation(SubModule):
    MAX_SPEED = 30

    def __init__(self, ship):
        self.module_name = "NAV"
        self.ship = ship
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

    def add_waypoint(self, dest):
        self.waypoints.append(dest)

    def get_pos(self):
        self.ship.get_pos()

    def status(self):
        course = math.degrees(self.course)
        if self.destination:
            return "Moving from {f} to {to}, course {c:d}, speed {s}".format(
                f=self.get_pos(), to=self.destination, s=self.speed, c=self.course)
        else:
            return "Stopped at {0}, course {1}".format(self.get_pos(), self.course)

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
