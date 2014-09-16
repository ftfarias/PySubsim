# -*- coding: utf-8 -*-
from sub_module import SubModule
from util import abs_angle_to_bearing, Bands
from physic import Point, MovableNewtonObject
import util
import math
import random


class SonarContact:
    NEW = 'New'
    TRACKING = 'Tracking'
    LOST = 'Lost'

    def __init__(self, sonar_idx):
        self.sonar_idx = sonar_idx
        self.tracking_status = self.NEW
        self.time_tracking = 0
        self.last_seen = None
        self.name = None  # like "i688"
        self.ident = ""  # like S1
        self.obj_type = None
        self.details = None
        self.range = None
        self.last_bearing = None
        self.bearings = []
        self.course = None
        self.speed = None
        self.blade_number = None   # Number of blades in the propeller
        self.blade_frequence = None   # Turns for second of the propeller
        self.knots_per_turn = 0
        self.deep = 0
        self.bands = [0.0] * 10

    def propeller_speed(self):
        if self.blade_frequence is None or self.knots_per_turn is None:
            return None
        return self.blade_frequence * self.knots_per_turn

    def is_new(self):
        return self.tracking_status == self.NEW

    def estimate_pos(self, ship_pos=None):
        if self.range is None:
            return None
        if ship_pos is None:
            ship_pos = Point(0,0)
        return ship_pos + Point(math.cos(self.last_bearing)*self.range, math.sin(self.last_bearing)*self.range)

    def new_bearing(self, time, bearing):
        self.last_bearing = bearing
        self.bearings.append((time, bearing))

    def __str__(self):
        obj_type = self.obj_type if self.obj_type else '<unknown>'
        course = round(self.course) if self.course else '-'
        range_str = round(self.range) if self.range else '-'
        speed = round(self.speed) if self.speed else '-'
        bearing = util.abs_angle_to_bearing(self.last_bearing)
        #dist = reference_pos.distance_to(pos)
        #angle = math.degrees(util.abs_angle_to_bearing(reference_pos.angle_to(pos)))
        return "{ident:3} ({ty}) bearing {bearing:3.0f}  range {range}  course {course}  speed {speed}  rel.pos:{pos}  <{status}>".\
            format(ident=self.ident, ty=obj_type, bearing=bearing, range=range_str,
            course=course, speed=speed, pos=self.estimate_pos(), status=self.tracking_status)


class Sonar(SubModule):
    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "SONAR"
        self.contacts = {}
        self.sea = sub.sea
        self.counter = 0  # counter for Sierra Contacts
        self.time_for_next_scan = 0

    def return_near_objects(self):
        return self.contacts

    def get_new_contact_id(self):
        self.counter += 1
        return "S{0:d}".format(self.counter)

    def guess_obj_type(self, bands):
        probs = []
        for known_obj in self.KNOWN_TYPES:
            name = known_obj[0]
            ref_bands = known_obj[1]
            likelihood = util.calc_band_likelihood(ref_bands, bands)
            probs.append((likelihood, name))
        print(probs)
        return probs

    def turn(self, time_elapsed):
        if self.time_for_next_scan <= 0.0:
            # passive scan
            self.passive_scan(time_elapsed)
            self.time_for_next_scan = 60.0
        else:
            self.time_for_next_scan -= time_elapsed

        #if self.mode == self.ACTIVE_SCAN:
        #    self.pulse_scan()

    def passive_scan(self, time_elapsed):
        scan = self.sea.passive_scan(self.sub, time_elapsed)
        for sr in scan:  #
            idx = sr.sonar_idx
            if idx in self.contacts:
                self.update_contact(self.contacts[idx], sr, time_elapsed)
            else:
                self.add_contact(sr)


    def pulse_scan(self):
        pass


    def add_contact(self, scan_result):
        sc = SonarContact(scan_result.sonar_idx)
        sc.new_bearing(self.sea.time, scan_result.bearing)
        sc.ident = self.get_new_contact_id()
        self.contacts[scan_result.sonar_idx] = sc
        self.add_message("New contact bearing {0:3.0f}, designated {1}".format(util.abs_angle_to_bearing(sc.last_bearing), sc.ident),True)


    def update_contact(self, sc, scan_result, time_elapsed):
        #sc.total_time_elapsed += time_elapsed
        if (sc.time_tracking < 10):
            sc.tracking_status = sc.NEW
        else:
            sc.tracking_status = sc.TRACKING
        sc.time_tracking += time_elapsed
        sc.last_seen = self.sub.sea.time
        #self.range = None
        sc.new_bearing(scan_result.bearing)
        #self.course = None
        #self.speed = None
        sc.deep = scan_result.deep
        sc.bands = [0.0] * 10
        pass

    def status(self):
        return "SONAR: tracking {objs} objects".format(objs=len(self.contacts))
