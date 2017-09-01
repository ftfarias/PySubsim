# -*- coding: utf-8 -*-
import logging
import random

import sea
import sea_object
from submarine.sub import Submarine
from util.physic import Point


logger = logging.getLogger("subsim")


class Scenario(object):
    def __init__(self):
        logger.debug("Sceneario Init")
        self.name = 'General'
        self.sea = None
        self.player_sub = None

    def initialize(self):
        logger.debug("Sceneario Initialization")
        self.sea = sea.Sea()


    def scenary_test_sonar(self):
        # for i in xrange(2):
        # whale = self.create_whale()
        #     self.sea.add_object(whale)

        # self.add_buoy(Point(3, 3), Bands({30: 100, 300: 80, 3000: 50}), deep=0)
        # self.add_buoy(Point(3, 4), Bands({30: 150, 300: 120, 3000: 100}), deep=0)
        # self.add_buoy(Point(4, 4), Bands({40: 100, 400: 80, 4000: 50}), deep=0)
        # self.add_buoy(Point(5, 5), Bands({50: 100, 500: 80, 5000: 50}), deep=0)
        # self.add_buoy(Point(7, 7), Bands({70: 100, 700: 80, 7000: 50}), deep=0)
        # self.add_buoy(Point(8, 8), Bands({80: 100, 800: 80, 8000: 50}), deep=0)

        logger.info("Creating Player Submarine")
        self.player_sub = Submarine(self.sea)
        self.player_sub.pos = Point(5, 5)
        self.player_sub.deep = 120
        self.player_sub.name = "USS Sant Paul"
        self.sea.add_object(self.player_sub)

        buoy = sea_object.SonarBuoy(self.sea, Point(1, 1), 100, 140, deep=0)
        self.sea.add_object(buoy)

        # dummy_ship = ShipFactory.create_simple_sub(sea, Point(30, 30))
        # sea.create_smallboat(dummy_ship)

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
        logger.debug("Creating a whale at {0}".format(pos))
        whale = Whale(self.sea)
        whale.pos = pos
        logger.debug("Whale {0}".format(whale))
        return whale

        # def create_warship(self, pos=None, ship_type=None):
        # t = ['Destroyer', 'Warship']
        # if pos is None:
        # pos = Point(random.randint(0, 10), random.randint(0, 10))
        # if ship_type is None:
        # ship_type = t[random.randint(0, len(t) - 1)]
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

