from sub import ShipFactory
from sea import Sea,SeaObject
from util import abs_angle_to_bearing, Bands
from physic import Point, MovableNewtonObject
import time
import sys

sea = Sea()
sub = ShipFactory.create_player_sub(sea)

sub.nav.set_destination(Point(11,11))
sub.nav.speed = 5

for _ in range(30):
    print("-"*20)
    sea.turn(0.1)
    print(sub.nav)
    print(sub)
    print("")
