import unittest

from part import Empty, Interval, INFINITY, Atomic


class MarkTestCase(unittest.TestCase):
    def test___str__(self):
        a = Atomic[int].from_tuple((4, 5))
        self.assertEqual(str(a.lower), "4")
        self.assertEqual(str(a.upper), "5-")
        a = Atomic[int].from_tuple((4, 5, None, True))
        self.assertEqual(str(a.lower), "4+")
        self.assertEqual(str(a.upper), "5")


class IntervalTestCase(unittest.TestCase):
    def test___new__(self):
        self.assertIs(
            Interval[int](lower_value=INFINITY, upper_value=-INFINITY), Empty[int]()
        )
        self.assertIs(Interval[int](upper_value=-INFINITY), Empty[int]())
        self.assertIs(Interval[int](lower_value=INFINITY), Empty[int]())
        self.assertIs(Interval[int](lower_value=1, upper_value=0), Empty[int]())
        self.assertIsInstance(Interval[int](lower_value=0), Interval)

    def test__init__(self):
        self.assertEqual(str(Interval[int]()), "(-inf;+inf)")
        self.assertEqual(str(Interval[int](0, 5)), "[0;5)")
        self.assertEqual(
            str(
                Interval[int](
                    lower_value="",
                    lower_closed=False,
                    upper_value="Hello World!",
                    upper_closed=False,
                )
            ),
            "('';'Hello World!')",
        )
        with self.assertRaises(ValueError):
            _ = Interval[int](lower_value=set("abc"), upper_value=set("bcd"))

    def test_from_tuple(self):
        self.assertEqual(str(Atomic[int].from_tuple((1,))), "[1;1]")
        self.assertEqual(str(Atomic[int].from_tuple((0, 1))), "[0;1)")
        self.assertEqual(str(Atomic[int].from_tuple((0, 1, None))), "(0;1)")
        self.assertEqual(str(Atomic[int].from_tuple((0, 1, True, True))), "[0;1]")
        self.assertEqual(str(Atomic[int].from_tuple((0, 1, None, True))), "(0;1]")

    def test_from_value(self):
        self.assertEqual(str(Atomic[int].from_value(1)), "[1;1]")
        self.assertEqual(str(Atomic[int].from_value(Empty[int]())), "")

    def test_lower_limit(self):
        self.assertEqual(str(Interval[int].lower_limit(value=1)), "[1;+inf)")
        self.assertEqual(
            str(Interval[int].lower_limit(value=1, closed=None)), "(1;+inf)"
        )

    def test_upper_limit(self):
        self.assertEqual(str(Interval[int].upper_limit(value=1)), "(-inf;1)")
        self.assertEqual(
            str(Interval[int].upper_limit(value=1, closed=True)), "(-inf;1]"
        )

    def test___bool__(self):
        self.assertTrue(bool(Interval[int]()))

    def test___hash__(self):
        self.assertEqual(hash(Interval[int]()), hash(Interval[int]()))

    def test___eq__(self):
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=4)
            == Interval[int](lower_value=0, upper_value=4)
        )
        self.assertTrue(Interval[int]() == Interval[int]())
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=4)
            == Interval[int](lower_value=0, upper_value=5)
        )
        self.assertFalse(Interval[int]() == 0)
        self.assertFalse(Interval[int]() == Empty[int]())

    def test___lt__(self):
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1)
            < Interval[int](lower_value=2, upper_value=3)
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1)
            < Interval[int](lower_value=1, upper_value=3)
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=1, upper_closed=True)
            < Interval[int](lower_value=1, upper_value=3)
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1, upper_closed=False)
            < Interval[int](lower_value=1, upper_value=3)
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1)
            < Interval[int](lower_value=1, lower_closed=False, upper_value=3)
        )
        self.assertFalse(Interval[int]() < Empty[int]())
        with self.assertRaises(TypeError):
            Interval[int]() < None

    def test___gt__(self):
        self.assertTrue(
            Interval[int](lower_value=2, upper_value=3)
            > Interval[int](lower_value=0, upper_value=1)
        )
        self.assertTrue(
            Interval[int](lower_value=1, upper_value=3)
            > Interval[int](lower_value=0, upper_value=1)
        )
        self.assertFalse(
            Interval[int](lower_value=1, upper_value=3)
            > Interval[int](lower_value=0, upper_value=1, upper_closed=True)
        )
        self.assertTrue(
            Interval[int](lower_value=1, upper_value=3)
            > Interval[int](lower_value=0, upper_value=1, upper_closed=False)
        )
        self.assertTrue(
            Interval[int](lower_value=1, lower_closed=False, upper_value=3)
            > Interval[int](lower_value=0, upper_value=1)
        )
        self.assertFalse(Interval[int]() > Empty[int]())
        with self.assertRaises(TypeError):
            Interval[int]() > None

    def test___or__(self):
        self.assertEqual(str(Interval[int](1, 3) | Interval[int](2, 4)), "[1;4)")
        self.assertEqual(
            str(Interval[int](1, 2) | Interval[int](3, 4)), "[1;2) | [3;4)"
        )

    def test___and__(self):
        self.assertEqual(str(Interval[int](1, 3) & Interval[int](2, 4)), "[2;3)")
        self.assertEqual(str(Interval[int](1, 2) & Interval[int](3, 4)), "")
        self.assertEqual(str(Interval[int](1, 3) & Empty[int]()), "")
        with self.assertRaises(TypeError):
            Interval[int](1, 3) & None

    def test___sub__(self):
        self.assertEqual(str(Interval[int](1, 3) - Interval[int](2, 4)), "[1;2)")
        self.assertEqual(str(Interval[int](1, 2) - Interval[int](1, 4)), "")
        self.assertEqual(str(Interval[int](1, 3) - Empty[int]()), "[1;3)")
        with self.assertRaises(TypeError):
            Interval[int](1, 3) - None

    def test___xor__(self):
        self.assertEqual(
            str(Interval[int](1, 3) ^ Interval[int](2, 4)), "[1;2) | [3;4)"
        )
        self.assertEqual(str(Interval[int](1, 2) ^ Interval[int](1, 4)), "[2;4)")
        self.assertEqual(str(Interval[int](1, 3) ^ Empty[int]()), "[1;3)")
        with self.assertRaises(TypeError):
            Interval[int](1, 3) ^ None

    def test___invert__(self):
        self.assertEqual(str(~Interval[int](0, 1)), "(-inf;0) | [1;+inf)")

    def test_before(self):
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1).before(
                Interval[int](lower_value=2, upper_value=3)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=2, upper_value=3).before(
                Interval[int](lower_value=0, upper_value=1), reverse=True
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1).before(
                Interval[int](lower_value=1, upper_value=3)
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=1, upper_closed=True).before(
                Interval[int](lower_value=1, upper_value=3)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1, upper_closed=True).before(
                Interval[int](lower_value=1, upper_value=3), strict=False
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1, upper_closed=False).before(
                Interval[int](lower_value=1, upper_value=3)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1).before(
                Interval[int](lower_value=1, lower_closed=False, upper_value=3)
            )
        )
        self.assertFalse(Interval[int]().before(Empty[int]()))
        with self.assertRaises(TypeError):
            Interval[int]().before(None)

    def test_meets(self):
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1, upper_closed=True).meets(
                Interval[int](lower_value=1, upper_value=2)
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=1, upper_closed=True).meets(
                Interval[int](lower_value=1, upper_value=2), reverse=True
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=1, upper_closed=False).meets(
                Interval[int](lower_value=1, upper_value=2)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=1, upper_closed=False).meets(
                Interval[int](lower_value=1, upper_value=2), strict=False
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=1).meets(
                Interval[int](lower_value=1, lower_closed=False, upper_value=2)
            )
        )
        self.assertFalse(Interval[int]().meets(Empty[int]()))
        with self.assertRaises(TypeError):
            Interval[int]().meets(None)

    def test_overlaps(self):
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=2).overlaps(
                Interval[int](lower_value=1, upper_value=3)
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=2).overlaps(
                Interval[int](lower_value=1, upper_value=3), reverse=True
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=2).overlaps(
                Interval[int](lower_value=0, upper_value=2)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=2).overlaps(
                Interval[int](lower_value=0, upper_value=2), strict=False
            )
        )
        self.assertFalse(Interval[int]().overlaps(Empty[int]()))
        with self.assertRaises(TypeError):
            Interval[int]().overlaps(None)

    def test_starts(self):
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=2).starts(
                Interval[int](lower_value=0, upper_value=3)
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=2).starts(
                Interval[int](lower_value=0, upper_value=3), reverse=True
            )
        )
        self.assertFalse(
            Interval[int](lower_value=0, upper_value=2).starts(
                Interval[int](lower_closed=False, lower_value=0, upper_value=3)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=0, upper_value=2).starts(
                Interval[int](lower_closed=False, lower_value=0, upper_value=3),
                strict=False,
            )
        )
        self.assertFalse(Interval[int]().starts(Empty[int]()))
        with self.assertRaises(TypeError):
            Interval[int]().starts(None)

    def test_during(self):
        self.assertTrue(
            Interval[int](lower_value=1, upper_value=2).during(
                Interval[int](lower_value=0, upper_value=3)
            )
        )
        self.assertFalse(
            Interval[int](lower_value=1, upper_value=2).during(
                Interval[int](lower_value=0, upper_value=3), reverse=True
            )
        )
        self.assertFalse(
            Interval[int](lower_value=1, upper_value=2).during(
                Interval[int](lower_value=1, upper_value=2)
            )
        )
        self.assertTrue(
            Interval[int](lower_value=1, upper_value=2).during(
                Interval[int](lower_value=1, upper_value=2), strict=False
            )
        )
        self.assertFalse(Interval[int]().during(Empty[int]()))
        with self.assertRaises(TypeError):
            Interval[int]().during(None)

    def test_finishes(self):
        self.assertTrue(
            Interval[int](lower_value=1, upper_value=2).finishes(
                Interval[int](lower_value=0, upper_value=2)
            )
        )
        self.assertFalse(
            Interval[int](lower_value=1, upper_value=2).finishes(
                Interval[int](lower_value=0, upper_value=2), reverse=True
            )
        )
        self.assertTrue(
            Interval[int](lower_value=1, upper_value=2).finishes(
                Interval[int](lower_value=0, upper_value=2, upper_closed=True),
                strict=False,
            )
        )
        self.assertFalse(
            Interval[int](lower_value=1, upper_value=2).finishes(
                Interval[int](lower_value=0, upper_value=2, upper_closed=True)
            )
        )
        self.assertFalse(Interval[int]().finishes(Empty[int]()))
        with self.assertRaises(TypeError):
            Interval[int]().finishes(None)

    def test_lower_value(self):
        self.assertEqual(Interval[int](lower_value=1, upper_value=2).lower_value, 1)

    def test_upper_value(self):
        self.assertEqual(Interval[int](lower_value=1, upper_value=2).upper_value, 2)

    def test_lower_closed(self):
        self.assertEqual(Interval[int](lower_value=1, upper_value=2).lower_closed, True)

    def test_upper_closed(self):
        self.assertEqual(Interval[int](lower_value=1, upper_value=2).upper_closed, None)

    if __name__ == "__main__":
        unittest.main()
