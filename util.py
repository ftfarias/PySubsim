import math
from typing import Tuple

Vector = Tuple[float, float]  # convenience alias
PI = math.pi

#############################
#        GAME ANGLES        #
#############################
# (1, -1)    ( 1, 0)    (1,  1)
# (0, -1)  <-( 0, 0)->  (0,  1)
# (-1,-1)    (-1, 0)    (-1, 1)

# reference frame [-pi, pi)
#  3/4*PI    |   PI/2    |   PI/4
#  PI or -PI |   center  |   0.00
# -3/4*PI    |  -PI/2    |  -PI/4

# reference frame [0, 2*pi)
# 3/4*PI   |   PI/2    |   PI/4
#     PI   |   center  |   0.00 or 2*PI
# 5/4*PI   |   3/2*PI  |   7/4*PI

# NW         North     NE
# West     <- 0, 0 ->  East
# SW         South     SE

#############################
#        USER ANGLES        #
#############################
# also known as bearing angles

# (1, -1)    ( 1, 0)    (1,  1)
# (0, -1)  <-( 0, 0)->  (0,  1)
# (-1,-1)    (-1, 0)    (-1, 1)

# NW         North     NE
# West     <- 0, 0 ->  East
# SW         South     SE

# directional angles in degrees
# 315   0    45
# 270   o    90
# 225  180   135


# all angles in radians, in the range [0, 2*pi) or [-pi, pi) using the "Game Angles" convention
def normalize_angle_pi(angle: float) -> float:
    """Normalize an angle in radians to the range [-pi, pi]."""
    return (angle + math.pi) % (2 * math.pi) - math.pi


def normalize_angle_2pi(angle: float) -> float:
    """Normalize an angle in radians to the range [0, 2*pi]."""
    return angle % (2 * math.pi)


def norm(v: Vector) -> float:
    """Euclidean norm of a 2-tuple."""
    x, y = v
    return math.hypot(x, y)


def angle(v: Vector) -> float:
    """Angle of a 2-tuple, in radians from North (y-axis up)."""
    x, y = v
    return math.atan2(x, y)  # swap so 0 = North, CCW positive


def vec_from_angle(theta: float, length: float = 1.0) -> Vector:
    """Return vector of given length pointing to theta (0 = North)."""
    # undo the swap done in angle()
    return (math.sin(theta) * length, math.cos(theta) * length)


def angle_to_bearing(angle: float) -> float:
    """Convert an angle in radians to a bearing in degrees."""
    angle_deg = math.degrees(angle)
    return (90.0 - angle_deg) % 360


def bearing_to_angle(bearing: float) -> float:
    """Convert a bearing in degrees to an angle in radians."""
    return math.radians((90.0 - bearing) % 360)


if __name__ == "__main__":
    # Test the functions
    assert math.isclose(normalize_angle_pi(3 * PI), -PI)
    assert math.isclose(normalize_angle_2pi(-math.pi / 2), 3 * math.pi / 2)
    assert math.isclose(norm((3, 4)), 5.0)
    assert math.isclose(angle((0, 1)), 0)  # 0 radians is North
    angules = [x for x in range(0, 720, 45)]  # angles in degrees
    for a in angules:
        angle_rad = bearing_to_angle(a)
        print(
            f"Bearing {a}: {angle_rad} radians, angle_to_bearing: {angle_to_bearing(angle_rad)} deg"
        )
        print(f"Vector from angle {a} degrees: {vec_from_angle(angle_rad, 1.0)}")
        print(
            f"normalize_angle_pi: {normalize_angle_pi(angle_rad)}, "
            f"normalize_angle_2pi: {normalize_angle_2pi(angle_rad)}"
        )

        print("-" * 40)



    # assert math.isclose(angle_to_bearing(math.pi / 3), 30.0)
    # assert math.isclose(bearing_to_angle(30), math.pi / 3)

    # print("Normalize angle to [-pi, pi]:", normalize_angle_pi(3 * math.pi))
    # print("Normalize angle to [0, 2*pi]:", normalize_angle_2pi(-math.pi / 2))
    # print("Norm of (3, 4):", norm((3, 4)))
    # print("Angle of (1, 0):", angle((1, 0)))
    # print("Vector from angle pi/4 with length 5:", vec_from_angle(math.pi / 4, 5))

    # print("Bearing from angle pi/3:", angle_to_bearing(math.pi / 3))
    # print("Angle from bearing 30 degrees:", bearing_to_angle(30))
