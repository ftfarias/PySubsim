# -*- coding: utf-8 -*-


# class Ship(MovableNewtonObject):
#     def __init__(self, drag_factor, max_turn_per_hour, max_acceleration):
#         super(Ship, self).__init__()
#         self._rudder = 0
#         self.max_turn_per_hour = max_turn_per_hour
#     self.drag_factor = drag_factor
#         self.frontal_drag_factor = drag_factor
#         self.drag_factor = drag_factor
#         self.drag_force = Point(0, 0)
#         self.turbine_acceleration = Point(0, 0)
#         self.turbine = Turbine(self, max_acceleration)






        # return self._velocity.angle

    # def set_course(self, angle):
    #     '''
    #     :param angle: new angle in radians
    #     :return: none
    #     '''
    #     angle = normalize_angle_2pi(angle)
    #     self._velocity.angle = angle
    #     self._acceleration.angle = self._velocity.angle  # assumes the rotation also changes the acceleration




    # def __str__(self):
    #     return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚) rudder:{rudder}".format(
    #         p=self._position,
    #         v=self._velocity,
    #         vt=self._velocity.angle,
    #         va=self._velocity.bearing,
    #         a=self._acceleration,
    #         at=self._acceleration.angle,
    #         aa=self._acceleration.bearing,
    #         rudder=self.rudder)
    #
    # def debug(self):
    #     return "pos:{p}  vel:{v}({vt:.1f};{va:.0f}˚)  accel:{a}({at:.1f};{aa:.0f}˚)".format(
    #         p=self._position,
    #         v=self._velocity,
    #         vt=self._velocity.angle,
    #         va=self._velocity.bearing,
    #         a=self._acceleration,
    #         at=self._acceleration.angle,
    #         aa=self._acceleration.bearing)
    #
    #
