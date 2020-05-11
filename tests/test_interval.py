import unittest

from part import Interval, INFINITY, EMPTY, Atomic


class MarkTestCase(unittest.TestCase):
    def test___str__(self):
        a = Atomic.from_tuple((4, 5))
        self.assertEqual(str(a.lower), "4")
        self.assertEqual(str(a.upper), "5-")
        a = Atomic.from_tuple((4, 5, None, True))
        self.assertEqual(str(a.lower), "4+")
        self.assertEqual(str(a.upper), "5")


class IntervalTestCase(unittest.TestCase):
    def test___new__(self):
        self.assertIs(Interval(lower_value=INFINITY, upper_value=-INFINITY), EMPTY)
        self.assertIs(Interval(upper_value=-INFINITY), EMPTY)
        self.assertIs(Interval(lower_value=INFINITY), EMPTY)
        self.assertIs(Interval(lower_value=1, upper_value=0), EMPTY)
        self.assertIsInstance(Interval(lower_value=0), Interval)

    def test__init__(self):
        self.assertEqual(str(Interval()), "(-inf;+inf)")
        self.assertEqual(str(Interval(0, 5)), "[0;5)")
        self.assertEqual(
            str(
                Interval(
                    lower_value="",
                    lower_closed=False,
                    upper_value="Hello World!",
                    upper_closed=False,
                )
            ),
            "('';'Hello World!')",
        )
        with self.assertRaises(ValueError):
            _ = Interval(lower_value=set("abc"), upper_value=set("bcd"))

    def test_from_tuple(self):
        self.assertEqual(str(Atomic.from_tuple((1,))), "[1;1]")
        self.assertEqual(str(Atomic.from_tuple((0, 1))), "[0;1)")
        self.assertEqual(str(Atomic.from_tuple((0, 1, None))), "(0;1)")
        self.assertEqual(str(Atomic.from_tuple((0, 1, True, True))), "[0;1]")
        self.assertEqual(str(Atomic.from_tuple((0, 1, None, True))), "(0;1]")

    def test_from_value(self):
        self.assertEqual(str(Atomic.from_value(1)), "[1;1]")
        self.assertEqual(str(Atomic.from_value(EMPTY)), "")

    def test_lower_limit(self):
        self.assertEqual(str(Interval.lower_limit(value=1)), "[1;+inf)")
        self.assertEqual(str(Interval.lower_limit(value=1, closed=None)), "(1;+inf)")

    def test_upper_limit(self):
        self.assertEqual(str(Interval.upper_limit(value=1)), "(-inf;1)")
        self.assertEqual(str(Interval.upper_limit(value=1, closed=True)), "(-inf;1]")

    def test___bool__(self):
        self.assertTrue(bool(Interval()))

    def test___hash__(self):
        self.assertEqual(hash(Interval()), hash(Interval()))

    def test___eq__(self):
        self.assertTrue(
            Interval(lower_value=0, upper_value=4)
            == Interval(lower_value=0, upper_value=4)
        )
        self.assertTrue(Interval() == Interval())
        self.assertFalse(
            Interval(lower_value=0, upper_value=4)
            == Interval(lower_value=0, upper_value=5)
        )
        self.assertFalse(Interval() == 0)
        self.assertFalse(Interval() == EMPTY)

    def test___lt__(self):
        self.assertTrue(
            Interval(lower_value=0, upper_value=1)
            < Interval(lower_value=2, upper_value=3)
        )
        self.assertTrue(
            Interval(lower_value=0, upper_value=1)
            < Interval(lower_value=1, upper_value=3)
        )
        self.assertFalse(
            Interval(lower_value=0, upper_value=1, upper_closed=True)
            < Interval(lower_value=1, upper_value=3)
        )
        self.assertTrue(
            Interval(lower_value=0, upper_value=1, upper_closed=False)
            < Interval(lower_value=1, upper_value=3)
        )
        self.assertTrue(
            Interval(lower_value=0, upper_value=1)
            < Interval(lower_value=1, lower_closed=False, upper_value=3)
        )
        self.assertFalse(Interval() < EMPTY)
        with self.assertRaises(TypeError):
            Interval() < None

    def test___gt__(self):
        self.assertTrue(
            Interval(lower_value=2, upper_value=3)
            > Interval(lower_value=0, upper_value=1)
        )
        self.assertTrue(
            Interval(lower_value=1, upper_value=3)
            > Interval(lower_value=0, upper_value=1)
        )
        self.assertFalse(
            Interval(lower_value=1, upper_value=3)
            > Interval(lower_value=0, upper_value=1, upper_closed=True)
        )
        self.assertTrue(
            Interval(lower_value=1, upper_value=3)
            > Interval(lower_value=0, upper_value=1, upper_closed=False)
        )
        self.assertTrue(
            Interval(lower_value=1, lower_closed=False, upper_value=3)
            > Interval(lower_value=0, upper_value=1)
        )
        self.assertFalse(Interval() > EMPTY)
        with self.assertRaises(TypeError):
            Interval() > None

    def test___or__(self):
        self.assertEqual(str(Interval(1, 3) | Interval(2, 4)), "[1;4)")
        self.assertEqual(str(Interval(1, 2) | Interval(3, 4)), "[1;2) | [3;4)")

    def test___and__(self):
        self.assertEqual(str(Interval(1, 3) & Interval(2, 4)), "[2;3)")
        self.assertEqual(str(Interval(1, 2) & Interval(3, 4)), "")
        self.assertEqual(str(Interval(1, 3) & EMPTY), "")
        with self.assertRaises(TypeError):
            Interval(1, 3) & None

    def test___sub__(self):
        self.assertEqual(str(Interval(1, 3) - Interval(2, 4)), "[1;2)")
        self.assertEqual(str(Interval(1, 2) - Interval(1, 4)), "")
        self.assertEqual(str(Interval(1, 3) - EMPTY), "[1;3)")
        with self.assertRaises(TypeError):
            Interval(1, 3) - None

    def test___xor__(self):
        self.assertEqual(str(Interval(1, 3) ^ Interval(2, 4)), "[1;2) | [3;4)")
        self.assertEqual(str(Interval(1, 2) ^ Interval(1, 4)), "[2;4)")
        self.assertEqual(str(Interval(1, 3) ^ EMPTY), "[1;3)")
        with self.assertRaises(TypeError):
            Interval(1, 3) ^ None

    def test___invert__(self):
        self.assertEqual(str(~Interval(0, 1)), "(-inf;0) | [1;+inf)")

    def test_meets(self):
        self.assertTrue(
            Interval(lower_value=0, upper_value=1, upper_closed=True).meets(
                Interval(lower_value=1, upper_value=2)
            )
        )
        self.assertFalse(
            Interval(lower_value=0, upper_value=1, upper_closed=False).meets(
                Interval(lower_value=1, upper_value=2)
            )
        )
        self.assertTrue(
            Interval(lower_value=0, upper_value=1, upper_closed=False).meets(
                Interval(lower_value=1, upper_value=2), strict=False
            )
        )
        self.assertFalse(
            Interval(lower_value=0, upper_value=1).meets(
                Interval(lower_value=1, lower_closed=False, upper_value=2)
            )
        )
        self.assertFalse(Interval().meets(EMPTY))
        with self.assertRaises(TypeError):
            Interval().meets(None)

    def test_overlaps(self):
        self.assertTrue(
            Interval(lower_value=0, upper_value=2).overlaps(
                Interval(lower_value=1, upper_value=3)
            )
        )
        self.assertFalse(
            Interval(lower_value=0, upper_value=2).overlaps(
                Interval(lower_value=0, upper_value=2)
            )
        )
        self.assertTrue(
            Interval(lower_value=0, upper_value=2).overlaps(
                Interval(lower_value=0, upper_value=2), strict=False
            )
        )
        self.assertFalse(Interval().overlaps(EMPTY))
        with self.assertRaises(TypeError):
            Interval().overlaps(None)

    def test_starts(self):
        self.assertTrue(
            Interval(lower_value=0, upper_value=2).starts(
                Interval(lower_value=0, upper_value=3)
            )
        )
        self.assertFalse(
            Interval(lower_value=0, upper_value=2).starts(
                Interval(lower_closed=False, lower_value=0, upper_value=3)
            )
        )
        self.assertTrue(
            Interval(lower_value=0, upper_value=2).starts(
                Interval(lower_closed=False, lower_value=0, upper_value=3), strict=False
            )
        )
        self.assertFalse(Interval().starts(EMPTY))
        with self.assertRaises(TypeError):
            Interval().starts(None)

    def test_during(self):
        self.assertTrue(
            Interval(lower_value=1, upper_value=2).during(
                Interval(lower_value=0, upper_value=3)
            )
        )
        self.assertFalse(
            Interval(lower_value=1, upper_value=2).during(
                Interval(lower_value=1, upper_value=2)
            )
        )
        self.assertTrue(
            Interval(lower_value=1, upper_value=2).during(
                Interval(lower_value=1, upper_value=2), strict=False
            )
        )
        self.assertFalse(Interval().during(EMPTY))
        with self.assertRaises(TypeError):
            Interval().during(None)

    def test_finishes(self):
        self.assertTrue(
            Interval(lower_value=1, upper_value=2).finishes(
                Interval(lower_value=0, upper_value=2)
            )
        )
        self.assertTrue(
            Interval(lower_value=1, upper_value=2).finishes(
                Interval(lower_value=0, upper_value=2, upper_closed=True), strict=False
            )
        )
        self.assertFalse(
            Interval(lower_value=1, upper_value=2).finishes(
                Interval(lower_value=0, upper_value=2, upper_closed=True)
            )
        )
        self.assertFalse(Interval().finishes(EMPTY))
        with self.assertRaises(TypeError):
            Interval().finishes(None)

    def test_lower_value(self):
        self.assertEqual(Interval(lower_value=1, upper_value=2).lower_value, 1)

    def test_upper_value(self):
        self.assertEqual(Interval(lower_value=1, upper_value=2).upper_value, 2)

    def test_lower_closed(self):
        self.assertEqual(Interval(lower_value=1, upper_value=2).lower_closed, True)

    def test_upper_closed(self):
        self.assertEqual(Interval(lower_value=1, upper_value=2).upper_closed, None)

    if __name__ == "__main__":
        unittest.main()
