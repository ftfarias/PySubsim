class Reading(object):
    def __init__(self, time, bearing, distance, pos, course, speed, deep, stn, sources):
        self.time = time
        self.bearing = bearing
        self.distance = distance
        self.pos = pos
        self.course = course
        self.speed = speed
        self.deep = deep
        self.stn = stn
        self.sources = sources

class Contact:
    NEW = 'New'
    TRACKING = 'Tracking'
    LOST = 'Lost'

    def __init__(self, sonar_idx):
        self.tracking_status = self.NEW
        self.name = None  # like "i688"
        self.id = ""  # like S1
        self.obj_type = None
        self.details = None

        self.history = []

        self.blade_number = None  # Number of blades in the propeller
        self.blade_frequence = None  # Turns for second of the propeller
        self.knots_per_turn = 0
        self.bands = Bands()

    def last_reading(self):
        return self.history[-1]

    def bearing(self):
        return self.last_reading().bearing

    def distance(self):
        return self.last_reading().distance

    def speed(self):
        return self.last_reading().speed

    def course(self):
        return self.last_reading().course

    def pos(self):
        return self.last_reading().pos

    def stn(self):
        return self.last_reading().stn

    # auxiliar functions

    def propeller_speed(self):
        if self.blade_frequence is None or self.knots_per_turn is None:
            return None
        return self.blade_frequence * self.knots_per_turn

    def is_new(self):
        return self.tracking_status == self.NEW

    def estimate_pos(self, ship_pos=None):
        if ship_pos is None:
            ship_pos = Point(0, 0)
        angle = self.bearing() - (math.pi / 2)
        return ship_pos + Point(math.cos(angle) * self.range(), math.sin(angle) * self.range())

    def mark(self, time, bearing, contact_range, stn, speed=None, course=None):
        time_elapsed_since_last = (time - self.time_history[-1]).seconds
        last_pos = self.pos()
        # time_delta = (time - self.start_tracking_time).seconds

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
        course_symbol = util.angles_to_unicode(
            abs_angle_to_bearing(self.course())) if self.course() is not None else '*'
        range_str = round(self.range(), 1) if self.range() is not None else '-'
        speed = round(self.speed()) if self.speed() is not None else '-'
        name = self.name if self.name else '<no name>'
        bearing = abs_angle_to_bearing(self.bearing())
        bearing_symbol = util.angles_to_unicode(bearing)
        return u"{ident:3} ({ty}) bearing {bearing:3.0f}{bs}  range {range:5.1f}  course {course:3.0f}{arrow}  speed {speed:4.1f}   stn {snt} \tpos:{pos}\t<{status}>\t{name}". \
            format(ident=self.id, ty=obj_type, bearing=bearing, range=range_str,
                   course=course, speed=speed, pos=self.pos(), status=self.tracking_status,
                   snt=self.stn(), arrow=course_symbol, bs=bearing_symbol, name=name)
