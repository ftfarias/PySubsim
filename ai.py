#from sub_navigation import Navigation
import random

from util.physic import Point


class ArtificialInteligence(object):
    def __init__(self, sea_object):
        self.sea_object = sea_object

    def turn(self, time_elapsed):
        pass

class AiRandomTraveller(ArtificialInteligence):
    def __init__(self, sea_object):
        ArtificialInteligence.__init__(self, sea_object)

    def turn(self, time_elapsed):
        ArtificialInteligence.turn(time_elapsed)
        current_pos = self.sea_object.pos
        if self.sea_object.nav.destination is None:
            self.sea_object.nav.destination = Point(random.randint(0,10),random.randint(0,10))
            self.sea_object.nav.speed = random.randint(3,8)



