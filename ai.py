#from sub_navigation import Navigation
from physic import Point
import random

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


class AiSnappingShrimp(ArtificialInteligence):
    def __init__(self, shrimp):
        ArtificialInteligence.__init__(self, shrimp)
        self.snapping = False
        self.counter = random.randint(3, 20) + random.gauss(5, 10)

    def turn(self, time_elapsed):
        ArtificialInteligence.turn(time_elapsed)
        self.counter -= time_elapsed
        if self.snapping:
            if self.counter <= 0:
                # Stop snapping
                self.snapping = False
                self.counter = random.randint(1, 10)+random.randint(1, 10)+random.randint(1, 10)
        else:
            # in silence
            if self.counter <= 0:
                # Stars to snapping
                self.snapping = True
                self.counter = random.gauss(8, 5)+random.gauss(12, 5)



