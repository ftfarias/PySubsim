#from sub_navigation import Navigation
from physic import Point
import random

class ArtificialInteligence(object):
    def __init__(self, ship):
        self.ship = ship

    def turn(self, time_elapsed):
        pass

class AiRandomTraveller(ArtificialInteligence):
    def __init__(self, ship):
        ArtificialInteligence.__init__(self, ship)

    def turn(self, time_elapsed):
        ArtificialInteligence.turn(time_elapsed)
        current_pos = self.ship.pos
        if self.ship.nav.destination is None:
            self.ship.nav.destination = Point(random.randint(0,10),random.randint(0,10))
            self.ship.nav.speed = random.randint(3,8)





