from util import abs_angle_to_bearing, Bands
from physic import Point, MovableNewtonObject
from sub_navigation import Navigation

class SurfaceShip(MovableNewtonObject):
    def __init__(self, sea):
        MovableNewtonObject.__init__(self)
        self.sea = sea
        self.navigation = Navigation(self)

    def get_deep(self):
        return self.z

    def get_pos(self):
        return self.pos

    def add_waypoint(self, dest):
        self.navigation.add_waypoint(dest)







