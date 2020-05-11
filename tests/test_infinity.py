import unittest

from part import INFINITY


class InfinityTestCase(unittest.TestCase):
    def test_infinity(self):
        self.assertIs(INFINITY, --INFINITY)
        self.assertIs(INFINITY, +INFINITY)
        self.assertIs(-INFINITY, +-INFINITY)
        self.assertEqual(hash(INFINITY), id(INFINITY))
        self.assertEqual(hash(-INFINITY), id(-INFINITY))

        self.assertTrue(INFINITY > -INFINITY)
        self.assertFalse(INFINITY < None)
        self.assertFalse(INFINITY <= None)
        self.assertTrue(INFINITY <= INFINITY)
        self.assertTrue(INFINITY >= None)

        self.assertTrue(-INFINITY < INFINITY)
        self.assertFalse(-INFINITY > None)
        self.assertFalse(-INFINITY >= None)
        self.assertTrue(-INFINITY >= -INFINITY)
        self.assertTrue(-INFINITY <= None)


if __name__ == "__main__":
    unittest.main()
