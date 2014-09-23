import unittest
import math

class LinearScale():
    def __init__(self):
        self._domain = [0, 1]
        self._range = [0, 1]
        self.left_span = 0.0
        self.right_span = 0.0
        self.scale_factor = 1.0

    def domain(self, d):
        self._domain = d
        self.__calc()
        return self

    def range(self, r):
        self._range = r
        self.__calc()
        return self

    def __calc(self):
        domain_span = self._domain[1] - self._domain[0]
        range_span = self._range[1] - self._range[0]
        self.scale_factor = float(range_span) / float(domain_span)

    def map(self, value):
        return self._range[0] + (value-self._domain[0])*self.scale_factor


"""
"Standard" character ramp for grey scale pictures, black -> white.

   "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. "
A more convincing but shorter sequence for representing 10 levels of grey is

   " .:-=+*#%@"

An obvious problem is the variation in apparant density between some typefaces.

" .oO0#"

Here are hex values of common grey-scale ASCII Characters in order from
    darkest to lightest:

    # = 23
    @ = 40
    8 = 38
    % = 25
    O = 4F
    o = 6F
    " = 22
    ; = 3B
    , = 2C
    ' = 27
    . = 2E
      = 20

"""

class AsciiLinearScale():
    def __init__(self, domain, ascii_scale=" .oO0#"):
        self.ascii_scale = ascii_scale
        l = len(ascii_scale)
        self.scaler = linear_scaler(domain,[0,l])
        self.domain = domain

    def map(self, value):
        if value <= self.domain[0]:
            return self.ascii_scale[0]

        if value >= self.domain[1]:
            return self.ascii_scale[-1]

        return self.ascii_scale[int(round(self.scaler(value)))]


def linear_scaler(domain, range):
    return LinearScale().domain(domain).range(range).map


class LinearScale2D():
    def __init__(self):
        self.ls_x = LinearScale()
        self.ls_y = LinearScale()

    def map(self, x, y):
        return self.ls_x.map(x), self.ls_y.map(y)


def linear_scaler2d(domain_x, range_x, domain_y, range_y):
    def fn(x,y):
        return (LinearScale().domain(domain_x).range(range_x).map(x),
                LinearScale().domain(domain_y).range(range_y).map(y))
    return fn


class TestLinear(unittest.TestCase):

    def setUp(self):
        pass

    def test_linearscale(self):
        a = LinearScale()
        self.assertEqual(a.map(0),0)
        self.assertEqual(a.map(0.5),0.5)
        self.assertEqual(a.map(1),1)

    def test_linearscaler(self):
        a = linear_scaler([0,1], [0, 10])
        self.assertEqual(a(0), 0)
        self.assertEqual(a(1), 10)
        self.assertEqual(a(0.5), 5)
        self.assertEqual(a(0.2), 2)

    def test_linearscaler_inv1(self):
        a = linear_scaler([1,0], [1,0])
        self.assertAlmostEqual(a(0), 0)
        self.assertAlmostEqual(a(0.5), 0.5)
        self.assertAlmostEqual(a(0.9), 0.9)
        self.assertAlmostEqual(a(0.2), 0.2)

    def test_linearscaler_cross(self):
        a = linear_scaler([1,0], [0,1])
        self.assertEqual(a(1), 0)
        self.assertEqual(a(0.5), 0.5)
        self.assertEqual(a(0.1), 0.9)
        self.assertEqual(a(0.2), 0.8)

    def test_linearscaler2(self):
        a = linear_scaler([10,0], [0,10])
        self.assertEqual(a(0), 10)
        self.assertEqual(a(5), 5)
        self.assertEqual(a(1), 9)
        self.assertEqual(a(2), 8)

    def test_linearscaler3(self):
        a = linear_scaler([10, 5], [20, 15])
        self.assertEqual(a(10), 20)
        self.assertEqual(a(5), 15)
        self.assertEqual(a(9), 19)
        self.assertEqual(a(8), 18)

    def test_linearscaler2d_1(self):
        a = linear_scaler2d([10, 5], [20, 15], [10,0], [0,10])
        self.assertEqual(a(10,10), (20,0))
        self.assertEqual(a(5,9), (15,1))
        self.assertEqual(a(9,5), (19,5))
        self.assertEqual(a(8,0), (18,10))


if __name__ == '__main__':
    unittest.main()