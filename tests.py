import unittest
from Palette import Palette
from Color import Color

""" Just run this file to test then
    1) coverage run tests.py
    2) coverage report -m --omit tests.py
 """


class TestPalette(unittest.TestCase):
    def setUp(self):
        self.test_palette = Palette()

    def test_load1(self):
        # тестируем загрузку палитры из файла и не из файла
        self.test_palette.load(1)
        self.assertEqual(next(self.test_palette.palette), "#000040")
        self.assertEqual(self.test_palette.gradient, 0)
        self.assertEqual(next(self.test_palette.palette), "#00003D")

    def test_load_3(self):
        self.test_palette.load(-3)
        self.assertEqual(
            self.test_palette.colours,
            ([-420.0, 861.42857143, -438.61904762, 241.88095238],
                [-936.0, 2131.71428571, -1183.42857143, 212.35714286],
                [-726.0, 1891.71428571, -1152.69047619, 221.4047619]))
        self.assertEqual(next(self.test_palette), "#EABEC8")
        self.assertEqual(self.test_palette.gradient, 0.01953125)

    def test_load_4(self):
        self.test_palette.load(-4)
        self.assertEqual(
            self.test_palette.colours,
            ([344.19642857, -366.33928571, 250.46428571],
                [42.85714286, -42.71428571, 19.14285714],
                [47.32142857, -47.17857143, 20.07142857]))


class TestColor(unittest.TestCase):
    """Palette is used in color"""
    def setUp(self):
        self.color = Color()

    def test_color(self):
        self.assertEqual(self.color.code, "#969696")
        self.assertEqual(self.color.color_dif, 30)

    def test_color_decode(self):
        self.color.code = "#000000"
        self.color.decode()
        self.assertEqual([self.color.red, self.color.green, self.color.blue], [0, 0, 0])

    def test_color_next(self):
        self.assertEqual(next(self.color), "#969696")
        self.assertEqual(len(next(self.color)), 7)

    def test_color_mut(self):
        self.color.random_color = -2
        next(self.color)
        for i in range(10):
            self.assertLess(self.color.red, 181)
            self.assertLess(self.color.green, 181)
            self.assertLess(self.color.blue, 181)
            self.assertGreater(self.color.red, 119)
            self.assertGreater(self.color.green, 119)
            self.assertGreater(self.color.blue, 119)

    def test_define_palette(self):
        self.color.define_palette(1)
        self.assertEqual(next(self.color.palette), "#000040")
        self.assertEqual(next(self.color.palette), "#00003D")

class TestPaint(unittest.TestCase):
    pass

if __name__ == "__main__":
    testSuite = unittest.TestSuite()
    testSuite.addTest(unittest.makeSuite(TestPalette))
    testSuite.addTest(unittest.makeSuite(TestColor))
    runner = unittest.TextTestRunner()
    runner.run(testSuite)
