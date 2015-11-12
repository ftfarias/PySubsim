from util import physic
import util

class navigable(object):
    def __init__(self, max_speed, max_turn_rate_hour):
        self.obj = physic.MovableNewtonObject()
        self._rudder = 0  # rudder in radians pe minute
        self.MAX_TURN_RATE_HOUR = max_turn_rate_hour  # max_radians per minute
        self.MAX_SPEED = max_speed # max_speed in knots

    def get_speed(self):
        return self.obj.length

    def _set_speed(self, value):
        value = util.limits(value, -self.MAX_SPEED, self.MAX_SPEED)
        self.obj.length = value

