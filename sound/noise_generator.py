from sound import broadband, sum_of_decibels

class FlatNoise(object):
    # a flat, constant sound level
    def __init__(self, lower_freq, upper_freq, decibels):
        self.lower = lower_freq
        self.upper = upper_freq
        self.level = decibels

    def noise(self, lower_freq, upper_freq):
        lb = max(lower_freq, self.lower)
        ub = min(upper_freq, self.upper)
        return broadband(self.level, lb, ub)



class NoiseGenerator(object):
    def __init__(self):
        # assert isinstance(sub, Submarine)
        self.narrowbands = {}
        self.broadbands = []

#     def narrowband(self):
#         return self.narrowbands

    def add_narrowband(self,freq,decibels):
        self.narrowbands[freq] = decibels


    def add_broadband(self,gen):
        self.broadbands.append(gen)

    def noise(self, lower_freq, upper_freq):
        p = []

        for b in self.broadbands:
            p.append(b.noise(lower_freq, upper_freq))

        for k,v in self.narrowbands:
            if lower_freq <= k <= upper_freq:
                p.append(v)

        return sum_of_decibels(p)