import unittest

class LinearScale1D():
    def __init__(self):
        self.domain = [0,1]
        self.range = [0,1]
        self.a = 0.0
        self.b = 1.0

    def c(self, p):
        return self.a + p * self.b

class LinearScale2D():
    def __init__(self):
        self.ls_x = LinearScale1D()
        self.ls_y = LinearScale1D()

    def c(self, x,y):
        return self.ls_x.c(x), self.ls_y.c(y)

class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_mov_speed(self):
        a = LinearScale1D()
        self.assertEqual(a.c(0),0)
        self.assertEqual(a.c(0.5),0.5)
        self.assertEqual(a.c(1),1)


if __name__ == '__main__':
    unittest.main()