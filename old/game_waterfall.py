from util.linear_scale import linear_scaler_with_limit
from util import angles_to_unicode, shift, ascii_gray, ascii_reset


class Waterfall(object):
    def __init__(self, sonar):
        self.asciiScaler = None
        self.set_waterfall_level(50, 70)
        self.sonar = sonar

    def set_waterfall_level(self, low, high):
        #self.asciiScaler = AsciiLinearScale([low,high], ascii_scale=".:;|$#").map
        #self.asciiScaler = AsciiLinearScale([low,high], ascii_scale=u"\u2591\u2592\u2593\u2588").map
        self.scaler = linear_scaler_with_limit([low, high], [250, 1])

    def print_sonar(self):
        #s = [self.asciiScaler(x.value) for x in player_sub.sonar.sonar_array(120)]
        line = [ascii_gray(".", int(round(self.scaler(d)))) for d in self.sonar.sonar_array(120)]
        return "[{0}{1}]".format("".join(shift(line, self.sonar.WATERFALL_STEPS / 2)), ascii_reset())


    def print_waterfall(self, compact=1, l=60, inverted=True):
        """
        Inverted watefall means the most recente events shows in th bottom, not in top
        """
        wf = self.sonar.waterfall[-l:]  # filters the last "l" events
        len_wf = len(wf)

        wf_c = []  # compact waterfall
        #print(wf)
        if len_wf == 0:
            print ("no sonar data")
            return

        idx = 0
        while idx < len_wf:
            # idx_compact in the number of sonar readings to be "compacted" for next printed line
            idx_compact = min(compact, len_wf - idx)
            total = [0.0] * 120
            for _ in xrange(idx_compact):  # compacts the display, calculanting the average
                wf_idx = wf[idx]
                for c in xrange(120):
                    total[c] += wf_idx[c]
                idx += 1

            #print(total)
            #line = [self.asciiScaler(d/idx_compact) for d in total]
            line = [ascii_gray(".", int(round(self.scaler(d / idx_compact)))) for d in total]

            wf_c.append("[{0}{1}]".format("".join(shift(line, self.sonar.WATERFALL_STEPS / 2)), ascii_reset()))

        if not inverted:
            wf_c.reverse()

        step = 360 / self.sonar.WATERFALL_STEPS
        header = [angles_to_unicode(i * step) for i in xrange(self.sonar.WATERFALL_STEPS)]
        print(" " + "".join(shift(header, self.sonar.WATERFALL_STEPS / 2)))

        for l in wf_c:
            print(l)


    def print_waterfall_1m(self):
        self.print_waterfall(compact=1, l=60)

    def print_waterfall_30m(self):
        self.print_waterfall(compact=30, l=1800)

    def print_waterfall_2h(self):
        self.print_waterfall(compact=120, l=7200)

