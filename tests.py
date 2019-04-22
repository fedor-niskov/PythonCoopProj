import unittest
from Palette import Palette


class TestPalette(unittest.TestCase):
    def test_load(self):
        test_palette = Palette()
        test_palette.load(1)
        self.assertEqual(next(test_palette.palette), "#000040")
        self.assertEqual(next(test_palette.palette), "#00003D")
        test_palette.load(-3)
        self.assertEqual(
            test_palette.colours,
            ([-420.0, 861.42857143, -438.61904762, 241.88095238],
                [-936.0, 2131.71428571, -1183.42857143, 212.35714286],
                [-726.0, 1891.71428571, -1152.69047619, 221.4047619]))


if __name__ == "__main__":
    testSuite = unittest.TestSuite()
    testSuite.addTest(unittest.makeSuite(TestPalette))

    runner = unittest.TextTestRunner()
    runner.run(testSuite)
