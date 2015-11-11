import physic
from util import limits

class Ship(physic.MovableNewtonObject):

    def get_rudder(self):
        return self._rudder

    def set_rudder(self, angle):
        angle = limits(angle, -self.MAX_TURN_RATE_HOUR, self.MAX_TURN_RATE_HOUR)
        self._rudder = angle

    rudder = property(get_rudder, set_rudder, "Rudder")

    def rudder_right(self):
        self.rudder = self.MAX_TURN_RATE_HOUR

    def rudder_left(self):
        self.rudder = -self.MAX_TURN_RATE_HOUR

    def rudder_center(self):
        self.rudder = 0