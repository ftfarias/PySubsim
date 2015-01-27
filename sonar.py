# -*- coding: utf-8 -*-
from sub_module import SubModule
from util import abs_angle_to_bearing, Bands, Deployable
from physic import Point
# from sub import Submarine
import util
import math

# class SonarReading(object):
#     def __init__(self, time, bearing, distance, pos, course, speed, deep, stn, sources):


class SonarContact:
    NEW = 'New'
    TRACKING = 'Tracking'
    LOST = 'Lost'

    def __init__(self, current_time, bearing, stn, pos, range):
        self.tracking_status = self.NEW
        self.name = None  # like "i688"
        self.id = ""  # like S1
        self.obj_type = ''
        self.details = ''

        self.blade_number = None  # Number of blades in the propeller
        self.blade_frequence = None  # Turns for second of the propeller
        self.knots_per_turn = 0
        self.bands = Bands()

        self.first_contacted_time = current_time
        self.last_contact_time = current_time
        self.bearing = bearing
        self.range = range  # yards
        self.pos = pos
        self.course = None  # radians
        self.speed = None  # in knots
        self.deep = None  # in feet
        self.stn = stn
        self.sources = '...'  # S - Spherical, H - Hull, T - Towed Array

    def noise(self):
        return self.bands.total_level()


    def propeller_speed(self):
        if self.blade_frequence is None or self.knots_per_turn is None:
            return None
        return self.blade_frequence * self.knots_per_turn

    def is_new(self):
        return self.tracking_status == self.NEW

    def estimate_pos(self, ship_pos=None):
        if ship_pos is None:
            ship_pos = Point(0, 0)
        angle = self.bearing - (math.pi / 2)
        return ship_pos + Point(math.cos(angle) * self.range, math.sin(angle) * self.range)

    def mark(self, time, bearing, range, stn, sub_pos, speed=None, course=None):
        time_elapsed_since_last = (time - self.last_contact_time).seconds
        last_pos = self.pos
        # time_delta = (time - self.start_tracking_time).seconds

        self.last_contact_time = time
        self.bearing = bearing
        if range is None:
            self.range = 10
        else:
            self.range = range

        last_pos = self.pos
        new_pos = self.estimate_pos(sub_pos)
        self.pos = new_pos

        if speed is None:
            # in knots
            self.speed = 3600 * last_pos.distance_to(new_pos) / time_elapsed_since_last
        else:
            self.speed = 0

        if course is None:
            course = last_pos.angle_to(new_pos)
        self.course = course
        self.stn = stn

    def __str__(self):
        obj_type = self.obj_type if self.obj_type is not None else '<unknown>'
        if self.course is not None:
            course_str = '{0:3.0f}'.format(abs_angle_to_bearing(self.course))
            course_symbol = util.angles_to_unicode(
                abs_angle_to_bearing(self.course))
        else:
            course_str = ' - '
            course_symbol = ' '
        range_str = round(self.range, 1) if self.range is not None else '-'
        speed_str = '{0:4.1f}'.format(self.speed) if self.speed is not None else '-'
        name = self.name if self.name else '<no name>'
        bearing = abs_angle_to_bearing(self.bearing)
        bearing_symbol = util.angles_to_unicode(bearing)
        # print(bearing)
        # print(range_str)
        # print(course_str)
        # print(self.tracking_status)
        # print(self.sources)

        return u"{ident:3} ({ty})  bearing {bearing:3.0f}{bs}  range {range}  course {course}{course_symbol}  speed {speed}  stn {snt}  src:{src}  pos:{pos}\t<{status}>\t{name}". \
            format(ident=self.id, ty=obj_type, bearing=bearing, bs=bearing_symbol,
                   range=range_str,
                   course=course_str, course_symbol=course_symbol,
                   speed=speed_str, snt=self.stn, src=self.sources,
                   pos=self.pos, status=self.tracking_status,
                   name=name)


class TowedArrayTB16(Deployable):
    """
    TB-16 Fat Line Towed Array (688)
    The TB-16 Fat Line Towed Array consists of a 1400
    pound accoustic detector array, some 3.5 inches in diameter
    and 240 feet long, towed on a 2,400 foot long cable
    0.37 inches in diameter weighing 450 pounds.
    """

    def __init__(self, sea):
        # Size: 2400 feet
        # deploy rate: 7 feet/sec (* 3600 for feet/hour)
        Deployable.__init__(self, 2400, 7 * 3600)
        self.sea = sea
        # minimal Signal-to-Noise level dectection in DB
        # Ex: 1 mean the signal must be 1db higher than noise to be distinguable
        self.min_detection_stn = 1

    def turn(self, time_elapsed):  # time in hours
        Deployable.turn(self, time_elapsed)

    def __str__(self):
        return "TB-16 {0} ({1} feet of {2} deployed)".format(self.state, self.deployed_size, self.total_size)


class HullSonarBQQ10():
    """
    Passive Hull Sonar
    """

    def __init__(self, sea):
        self.sea = sea
        # minimal Signal-to-Noise level dectection in DB
        # Ex: 1 mean the signal must be 1db higher than noise to be distinguable
        self.min_detection_stn = 1


class SphereSonarBQQ10():
    """
    Passive Sphere Sonar
    """

    def __init__(self, sea):
        self.sea = sea
        # minimal Signal-to-Noise level dectection in DB
        # Ex: 1 mean the signal must be 1db higher than noise to be distinguable
        self.min_detection_stn = 1


class Sonar(SubModule):
    MAX_WATERFALL_HISTORY_SECONDS = 2 * 3600  # two hours
    WATERFALL_STEPS = 120
    # Spherical
    # Hull
    # Towed
    """
    The Seawolf has two towed arrays the TB-29 and the TB-16.
    In general, the TB-29 is longer and more sensitive than the TB-16,
    but the TB-16 remains effective at higher speeds.
    Select the Starboard Towed Array to deploy the TB-29 array.
    Select the Port Towed Array to deploy the TB-16.

    Also fitted are TB-16 surveillance and TB-29 tactical towed arrays,
    which will be replaced by the TB-29A thin-line towed array being
    developed by Lockheed Martin, and BQS 24 active sonar for close range detection.

    http://www.globalsecurity.org/military/systems/ship/systems/towed-array.htm
    """


    def __init__(self, sub):
        SubModule.__init__(self, sub)
        # assert isinstance(sub, Submarine)
        self.module_name = "SONAR"
        self.contacts = {}
        self.sea = sub.sea  # auxiliar
        self.counter = 0  # counter for Sierra Contacts
        self.time_for_next_update = 0
        self.time_for_next_waterfall = 0
        self.spherical = SphereSonarBQQ10(sea=self.sea)
        self.hull = HullSonarBQQ10(sea=self.sea)
        self.towed = TowedArrayTB16(sea=self.sea)

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
        self.towed.turn(time_elapsed)
        if self.time_for_next_update <= 0.0:
            # passive scan
            self.passive_scan()
            self.time_for_next_update = 10.0 / 3600  # every 10 seconds
        else:
            self.time_for_next_update -= time_elapsed

        if self.time_for_next_waterfall <= 0.0:
            self.waterfall_update()
            self.time_for_next_waterfall = 1.0 / 3600  # every second
        else:
            self.time_for_next_waterfall -= time_elapsed


            # if self.mode == self.ACTIVE_SCAN:
            #    self.pulse_scan()

    # def passive_scan(self, time_elapsed):
    #     scan = self.sea.passive_scan(self.sub, time_elapsed)
    #     for k, c in self.contacts.items():
    #         c.tracking_status = SonarContact.LOST
    #
    #     for sr in scan:  #
    #         idx = sr.sonar_idx
    #         if idx in self.contacts:
    #             self.update_contact(self.contacts[idx], sr, time_elapsed)
    #         else:
    #             self.add_contact(sr)


    def passive_scan(self):
        # Sphere Array
        spherical_scan = self.sea.passive_scan(self.sub, self.spherical)
        hull_scan = self.sea.passive_scan(self.sub, self.hull)
        # if towed array is deployed more than 90%, use it
        if self.towed.percent_deployed > 0.9:
            towed = self.sea.passive_scan(self.sub, self.towed)
        else:
            towed = []



        for k, c in self.contacts.items():
            c.tracking_status = SonarContact.LOST

        for sr in spherical_scan:  #
            idx = sr.object_idx
            if idx in self.contacts:
                self.update_contact(self.contacts[idx], sr)
            else:
                self.add_contact(sr)

    def add_contact(self, scan_result):
        sc = SonarContact(self.sea.time, scan_result.bearing, scan_result.signal_to_noise, Point(0, 0),
                          scan_result.range)
        sc.id = self.get_new_contact_id()
        sc.bands = scan_result.bands
        sc.blade_number = scan_result.blades
        sc.deep = scan_result.deep
        sc.tracking_status = sc.NEW
        st = "surface" if sc.deep == 0 else "submerged"

        self.contacts[scan_result.object_idx] = sc
        self.add_message("Conn, Sonar: New {st} contact on sonar, bearing {br:3.0f}, designated {d}".format(
            st=st, br=util.abs_angle_to_bearing(scan_result.bearing), d=sc.id), True)

    def update_contact(self, sonar_contact, scan_result):
        sonar_contact.tracking_status = sonar_contact.TRACKING

        time_elapsed_since_last = (self.sea.time - sonar_contact.last_contact_time).seconds
        # print(time_elapsed_since_last)

        last_pos = sonar_contact.pos
        # print(last_pos)

        sonar_contact.last_contact_time = self.sea.time
        sonar_contact.bearing = scan_result.bearing

        if scan_result.range is None:
            sonar_contact.range = 10
        else:
            sonar_contact.range = scan_result.range

        new_pos = sonar_contact.estimate_pos(self.sub.pos)
        sonar_contact.pos = new_pos
        sonar_contact.speed = 3600 * last_pos.distance_to(new_pos) / time_elapsed_since_last
        sonar_contact.course = last_pos.angle_to(new_pos)
        sonar_contact.stn = scan_result.signal_to_noise
        sonar_contact.deep = scan_result.deep
        sonar_contact.blade_number = scan_result.blades
        sonar_contact.bands = scan_result.bands


    def waterfall_update(self):
        s = [x.value for x in self.sonar_array(self.WATERFALL_STEPS)]
        self.waterfall.append(s)
        if len(self.waterfall) > self.MAX_WATERFALL_HISTORY_SECONDS:
            self.waterfall = self.waterfall[-self.MAX_WATERFALL_HISTORY_SECONDS]


    def pulse_scan(self):
        pass


    def noise_by_angle(self, from_angle, to_angle):
        sea_noise = self.sea.get_background_noise()
        sub_noise = self.sub.self_noise()
        backgroung_noise = sea_noise + sub_noise
        for k, obj in self.contacts:
            angle = obj.bearing
            # if from_angle <= angle <= to_angle:
        return backgroung_noise

    def sonar_array(self, num_angles):
        def backgroung_noise(self):
            sea_noise = self.sea.get_background_noise()
            sub_noise = self.sub.self_noise()
            return sea_noise + sub_noise

        step = 360 / num_angles
        angles = util.angles(num_angles)
        noise = [backgroung_noise(self) for _ in xrange(num_angles)]

        for k, obj in self.contacts.items():
            # print(obj.bearing())
            x = int(math.degrees(obj.bearing) / step)
            #print(x)
            noise[x] += obj.noise()

        # print(noise)
        return noise

    def deploy_towed_array(self):
        self.towed.deploy()

    def stop_towed_array(self):
        self.towed.stop()

    def retrieve_towed_array(self):
        self.towed.retrieve()

    def status(self):
        return "SONAR: tracking {objs} objects. Towed array: {towed}".format(objs=len(self.contacts), towed=self.towed)