
from util.deployable import Deployable
import math
from util.util import normalize_angle_pi


class TowerArray(Deployable):
    TOWED_ARRAY_DEPLOY_SPEED = 100 * 60  # 100 feet per minute

    def __init__(self, size, deploy_rate, inicial_deployed_size=0):
        super().__init__(size, deploy_rate, inicial_deployed_size)
        self.description = 'generic towed array'

class SphericalArray(object):
    LISTENING_ANGLE_MIN = math.radians(-150) + 2.0 * math.pi
    LISTENING_ANGLE_MAX = math.radians(150)
    MAX_SPEED = 25  # Knots

    # sensible to 300 degrees, centered in the bow
    def is_listening(self, angle):
        angle = normalize_angle_pi(angle)
        if self.LISTENING_ANGLE_MIN <= angle <= self.LISTENING_ANGLE_MAX:
            return True

        return False


class ANBQS13SphericalArray(SphericalArray):
    FREQUENCY_RANGE = (750, 2000)

    def __init__(self):
        self.description = 'AN/BQS-13'
        # self.gain_scaler_1 = linear_scaler_with_limit([math.log10(200), math.log10(1000)], [0, 15])


class ANBQQ5SphericalArray(SphericalArray):
    FREQUENCY_RANGE = (750, 2000)  # Hz

    def __init__(self):
        self.description = 'AN/BQQ-5'


class ANBQQ5HullArray(object):
    FREQUENCY_RANGE = (50, 1000)  # Hz
    MAX_SPEED = 32  # Knots

    def __init__(self):
        self.description = 'AN/BQQ-5'

    def is_listening(self, angle):
        return True
        # if angle > 30 and angle < 60:
        #     return True
        #
        # if angle > -60 and angle < -30:
        #     return True
        #
        # return False



class TD16DTowedArray(TowerArray):
    TOTAL_LENGTH = 2400 + 240
    DEPLOY_TIME = 40  # minutes
    DEPLOY_RATE = TOTAL_LENGTH / (DEPLOY_TIME * 60)
    FREQUENCY_RANGE = (10, 1000)  # Hz
    MAX_SPEED = 32  # Knots


    """ 
    TB-16 Fat Line Towed Array
    
    Used By Seawolf class submarines

    The TB-16 Fat Line Towed Array consists of a 1400 pound 
      accoustic detector array, some 3.5 inches in diameter and 240 feet long, towed on a
      2,400 foot long cable 0.37 inches in diameter weighing 450 pounds.

    Medium range 
    low-frequency
    2600 foot 3.5 inches/ 89mm thick
    hydrophones in the last 240 foot
    
    max distance: 18.000 yards / 9.1 NM
    
    Deploy time: (based on TB-23F) < 40 minutes
    Retrieval time: (based on TB-23F) < 20 minutes
    """

    def __init__(self, inicial_deployed_size=0):
        super().__init__(self.TOTAL_LENGTH, self.DEPLOY_RATE, inicial_deployed_size)
        self.description = 'TB-16 Fat Line'

    def is_listening(self, angle):
        if self.percent_deployed < 0.9:
            return False

        return True


