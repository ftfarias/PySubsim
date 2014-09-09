class SubModule:
    def __init__(self, sub):
        self.module_name = "<None>"
        self.sub = sub

    def add_message(self, msg, stop=False):
        self.sub.add_message(self.module_name, msg, stop)

    def turn(self, time_elapsed):
        pass

    def get_status(self):
        return "OK"


