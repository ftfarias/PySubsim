import random


class Sea(object):
    def __init__(self):
        pass


    def turn(self, time_elapsed, messages):
        self.background_noise = 90

        messages['sea_background_noise'] =  self.background_noise

