
class TimedValue(object):

    def __init__(self, initial_value, target_value, speed):
        self.current_value = initial_value
        self.target_value = target_value
        self.speed = speed

    def update(self, time_elapsed):
        if self.current_value < self.target_value:
            new_value = self.current_value + (time_elapsed * self.speed)
            if new_value > self.target_value:
                self.current_value = self.target_value
            else:
                self.current_value = new_value

        elif self.current_value > self.target_value:
            new_value = self.current_value - (time_elapsed * self.speed)
            if new_value < self.target_value:
                self.current_value = self.target_value
            else:
                self.current_value = new_value


