# -*- coding: utf-8 -*-
from sub_module import SubModule
from util import abs_angle_to_bearing, Bands
from physic import Point, MovableNewtonObject
from sound import db
import util
import math
import random


class SonarContact:
    NEW = 'New'
    TRACKING = 'Tracking'
    LOST = 'Lost'

    def __init__(self, sonar, sonar_idx):
        self.noise = db(db=random.randint(50,70))
        self.sonar_idx = sonar_idx
        self.sonar = sonar
        self.sub = sonar.sub
        self.sea = sonar.sub.sea
        self.tracking_status = self.NEW
        self.name = None  # like "i688"
        self.ident = ""  # like S1
        self.obj_type = None
        self.details = None

        self.time_history = []
        self.range_history = []
        self.bearings_history = []
        self.pos_history = []
        self.course_history = []
        self.speed_history = []
        self.stn_history = []

        self.blade_number = None   # Number of blades in the propeller
        self.blade_frequence = None   # Turns for second of the propeller
        self.knots_per_turn = 0
        self.deep = 0
        self.bands = Bands()

    def bearing(self):
        return self.bearings_history[-1]

    def range(self):
        return self.range_history[-1]

    def speed(self):
        return self.speed_history[-1]

    def course(self):
        return self.course_history[-1]

    def pos(self):
        return self.pos_history[-1]

    def stn(self):
        return self.stn_history[-1]

    # auxiliar functions

    def propeller_speed(self):
        if self.blade_frequence is None or self.knots_per_turn is None:
            return None
        return self.blade_frequence * self.knots_per_turn

    def is_new(self):
        return self.tracking_status == self.NEW

    def estimate_pos(self, ship_pos=None):
        if ship_pos is None:
            ship_pos = Point(0,0)
        angle = self.bearing() - (math.pi/2)
        return ship_pos + Point(math.cos(angle)*self.range(), math.sin(angle)*self.range())

    def mark(self, time, bearing, contact_range, stn, speed=None, course=None):
        time_elapsed_since_last = (time - self.time_history[-1]).seconds
        last_pos = self.pos()
        #time_delta = (time - self.start_tracking_time).seconds

        self.time_history.append(time)
        self.bearings_history.append(bearing)
        self.range_history.append(contact_range)

        new_pos = self.estimate_pos(self.sub.pos)
        self.pos_history.append(new_pos)

        if speed is None:
            speed = 3600 * last_pos.distance_to(new_pos) / time_elapsed_since_last
        self.speed_history.append(speed)

        if course is None:
            course = last_pos.angle_to(new_pos)
        self.course_history.append(course)

        self.stn_history.append(stn)

    def __str__(self):
        obj_type = self.obj_type if self.obj_type is not None else '<unknown>'
        course = abs_angle_to_bearing(self.course()) if self.course() is not None else '-'
        course_symbol = util.angles_to_unicode(abs_angle_to_bearing(self.course())) if self.course() is not None else '*'
        range_str = round(self.range(), 1) if self.range() is not None else '-'
        speed = round(self.speed()) if self.speed() is not None else '-'
        name = self.name if self.name else '<no name>'
        bearing = abs_angle_to_bearing(self.bearing())
        bearing_symbol = util.angles_to_unicode(bearing)
        return u"{ident:3} ({ty}) bearing {bearing:3.0f}{bs}  range {range:5.1f}  course {course:3.0f}{arrow}  speed {speed:4.1f}   stn {snt} \tpos:{pos}\t<{status}>\t{name}".\
            format(ident=self.ident, ty=obj_type, bearing=bearing, range=range_str,
            course=course, speed=speed, pos=self.pos(), status=self.tracking_status,
            snt=self.stn(), arrow=course_symbol, bs=bearing_symbol, name=name)


class Sonar(SubModule):
    MAX_WATERFALL_HISTORY_SECONDS = 2 * 3600  # two hours
    WATERFALL_STEPS = 120

    def __init__(self, sub):
        SubModule.__init__(self, sub)
        self.module_name = "SONAR"
        self.contacts = {}
        self.sea = sub.sea
        self.counter = 0  # counter for Sierra Contacts
        self.time_for_next_update = 0
        self.time_for_next_waterfall = 0
        self.waterfall = []


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

    def turn(self, time_elapsed):  # time in hours
        if self.time_for_next_update <= 0.0:
            # passive scan
            self.passive_scan(time_elapsed)
            self.time_for_next_update = 10.0 / 3600 # every 10 seconds
        else:
            self.time_for_next_update -= time_elapsed

        if self.time_for_next_waterfall <= 0.0:
            # passive scan
            self.waterfall_update()
            self.time_for_next_waterfall = 1.0 / 3600 # every second
        else:
            self.time_for_next_waterfall -= time_elapsed


        #if self.mode == self.ACTIVE_SCAN:
        #    self.pulse_scan()

    def passive_scan(self, time_elapsed):
        scan = self.sea.passive_scan(self.sub, time_elapsed)
        for k,c in self.contacts.items():
            c.tracking_status = SonarContact.LOST

        for sr in scan:  #
            idx = sr.sonar_idx
            if idx in self.contacts:
                self.update_contact(self.contacts[idx], sr, time_elapsed)
            else:
                self.add_contact(sr)

    def waterfall_update(self):
        s = [x.value for x in self.sonar_array(self.WATERFALL_STEPS)]
        self.waterfall.append(s)
        if len(self.waterfall) > self.MAX_WATERFALL_HISTORY_SECONDS:
            self.waterfall = self.waterfall[-self.MAX_WATERFALL_HISTORY_SECONDS]


    def pulse_scan(self):
        pass

    def add_contact(self, scan_result):
        sc = SonarContact(self, scan_result.sonar_idx)
        sc.time_history.append(self.sea.time)
        sc.ident = self.get_new_contact_id()
        sc.bands = scan_result.bands

        sc.bearings_history.append(scan_result.bearing)
        sc.range_history.append(scan_result.range)
        sc.pos_history.append(sc.estimate_pos(self.sub.pos))
        sc.stn_history.append(scan_result.signal_to_noise)
        sc.speed_history.append(0.0)
        sc.course_history.append(0.0)
        sc.blade_number = scan_result.blades
        sc.deep = scan_result.deep
        sc.tracking_status = sc.NEW

        if sc.deep == 0:
            st = "surface"
        else:
            st = "submerged"

        self.contacts[scan_result.sonar_idx] = sc
        self.add_message("Conn, Sonar: New {st} contact on sonar, bearing {br:3.0f}, designated {d}".format(
            st=st, br=util.abs_angle_to_bearing(scan_result.bearing), d=sc.ident), True)

    def update_contact(self, sc, scan_result, time_elapsed):
        sc.tracking_status = sc.TRACKING
        sc.mark(self.sea.time, scan_result.bearing, scan_result.range, scan_result.signal_to_noise)
        sc.deep = scan_result.deep
        sc.blade_number = scan_result.blades
        sc.bands = scan_result.bands

    def noise_by_angle(self, from_angle, to_angle):
        sea_noise = self.sea.get_background_noise()
        sub_noise = self.sub.self_noise()
        backgroung_noise = sea_noise + sub_noise
        for k, obj in self.contacts:
            angle = obj.bearing
            #if from_angle <= angle <= to_angle:

        return backgroung_noise



    def sonar_array(self, num_angles):
        def backgroung_noise(self):
            sea_noise = self.sea.get_background_noise()
            sub_noise = self.sub.self_noise()
            return sea_noise + sub_noise

        step = 360/num_angles
        angles = util.angles(num_angles)
        noise = [backgroung_noise(self) for _ in xrange(num_angles)]

        for k, obj in self.contacts.items():
            #print(obj.bearing())
            x = int(math.degrees(obj.bearing())/step)
            #print(x)
            noise[x] += obj.noise

        #print(noise)
        return noise


    def status(self):
        return "SONAR: tracking {objs} objects".format(objs=len(self.contacts))