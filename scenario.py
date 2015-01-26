import logging
import random

import sea
from sea_object import Whale
from sub import Submarine
from physic import Point


class Scenario(object):
    def __init__(self):
        self.name = 'General'
        self.sea = None
        self.player_sub = None

    def initialize(self):
        self.sea = sea.Sea()
        for i in xrange(2):
            whale = self.create_whale()
            self.sea.add_object(whale)

        print("Creating Player Submarine")
        self.player_sub = Submarine(self.sea)
        self.player_sub.pos = Point(6, 6)
        self.player_sub.deep = 120
        self.player_sub.name = "USS Sant Paul"
        self.sea.add_object(self.player_sub)

        #dummy_ship = ShipFactory.create_simple_sub(sea, Point(30, 30))
            #sea.create_smallboat(dummy_ship)

        """
        dummy_ship = ShipFactory.create_simple_ship(universe, Point(0, 1))
        universe.add_ship(dummy_ship)
        dummy_ship = ShipFactory.create_simple_ship(universe, Point(-1, 0))
        universe.add_ship(dummy_ship)
        dummy_ship = ShipFactory.create_simple_ship(universe, Point(0, -1))
        universe.add_ship(dummy_ship)
        dummy_ship = ShipFactory.create_simple_ship(universe, Point(1, 1))
        universe.add_ship(dummy_ship)
        dummy_ship = ShipFactory.create_simple_ship(universe, Point(2, 8))
        universe.add_ship(dummy_ship)
        """

        # for i in xrange(3):
        #     sea.create_fishing()
        #
        # for i in xrange(2):
        #     sea.create_warship()
        #
        # ship = sea.create_fishing(pos=Point(5,5))
        # ship.set_destination(0, 1)

        # game_loop(1, 0.1)
        #
        # def create_simple_sub(sea, pos):
        # sub = Submarine(sea)
        #     sub.set_speed(1)
        #     sub.actual_deep = random.randint(50, 300)
        #     sub.set_destination(Point(random.randint(0, 60), random.randint(0, 60)))
        #     sub.pos = pos
        #     return sub

    def create_whale(self, pos=None):
        if pos is None:
            pos = Point(random.randint(0, 10), random.randint(0, 10))
        logging.debug("Creating a whale at {0}".format(pos))
        whale = Whale(self.sea)
        whale.pos = pos
        logging.debug("Whale {0}".format(whale))
        return whale

        # def create_warship(self, pos=None, ship_type=None):
        # t = ['Destroyer', 'Warship']
        # if pos is None:
        #         pos = Point(random.randint(0, 10), random.randint(0, 10))
        #     if ship_type is None:
        #         ship_type = t[random.randint(0, len(t) - 1)]
        #     ship = MovableSeaObject(ship_type, pos)
        #     ship.set_destination(random.randint(0, 359), random.randint(5, 15))
        #     self.objects.append(ship)
        #     return ship

        # def create_fishing(self, pos=None, ship_type=None):
        #     t = ['Fishing Boat', 'Fishing Ship']
        #     if pos is None:
        #         pos = Point(random.randint(0, 10), random.randint(0, 10))
        #     if ship_type is None:
        #         ship_type = t[random.randint(0, len(t) - 1)]
        #     ship = MovableSeaObject(ship_type, pos)
        #     ship.set_destination(random.randint(0, 359), random.randint(1, 5))
        #     self.objects.append(ship)
        #     return ship

