import unittest
import math

class LinearScale():
    def __init__(self):
        self._domain = [0, 1]
        self._range = [0, 1]
        self.left_span = 0.0
        self.right_span = 0.0
        self.scale_factor = 1.0
        self.reverse_input = False
        self.reverse_output = False

    def domain(self,r):
        self._range = r
        self.__calc()
        return self

    def range(self,d):
        self._domain = d
        self.__calc()
        return self

    def __calc(self):
        domain_span = self._domain[1] - self._domain[0]
        range_span = self._range[1] - self._range[0]
        self.scale_factor = float(domain_span) / float(range_span)

    def map(self, value):
        return self._range[0] + (value-self._domain[0])*self.scale_factor


def linear_scaler(domain, range):
    return LinearScale().domain(domain).range(range).map


class LinearScale2D():
    def __init__(self):
        self.ls_x = LinearScale()
        self.ls_y = LinearScale()

    def map(self, x,y):
        return self.ls_x.map(x), self.ls_y.map(y)

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


if __name__ == '__main__':
    unittest.main()