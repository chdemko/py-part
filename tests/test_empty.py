import unittest

from part import Empty, Interval, FrozenIntervalSet, Atomic


class IntervalTestCase(unittest.TestCase):
    def test___bool__(self):
        self.assertFalse(bool(Empty[int]()))

    def test___hash__(self):
        self.assertEqual(hash(Empty[int]()), id(Empty[int]()))

    def test___eq__(self):
        self.assertEqual(Empty[int](), Empty[int]())
        self.assertNotEqual(Empty[int](), None)

    def test___lt__(self):
        self.assertFalse(Empty[int]() < Empty[int]())
        self.assertFalse(Empty[int]() < Interval[int]())
        with self.assertRaises(TypeError):
            Empty[int]() < None

    def test___gt__(self):
        self.assertFalse(Empty[int]() > Empty[int]())
        self.assertFalse(Empty[int]() > Interval[int]())
        with self.assertRaises(TypeError):
            Empty[int]() > None

    def test___or__(self):
        self.assertEqual(Empty[int]() | Empty[int](), FrozenIntervalSet[int]())
        self.assertEqual(
            Empty[int]() | Atomic[int].from_value(5), FrozenIntervalSet[int]([5])
        )
        with self.assertRaises(TypeError):
            Empty[int]() | None

    def test___and__(self):
        self.assertEqual(Empty[int]() & Empty[int](), FrozenIntervalSet[int]())
        self.assertEqual(
            Empty[int]() & Atomic[int].from_value(5), FrozenIntervalSet[int]()
        )
        with self.assertRaises(TypeError):
            Empty[int]() & None

    def test___sub__(self):
        self.assertEqual(Empty[int]() - Empty[int](), FrozenIntervalSet[int]())
        self.assertEqual(
            Empty[int]() - Atomic[int].from_value(5), FrozenIntervalSet[int]()
        )
        with self.assertRaises(TypeError):
            Empty[int]() - None

    def test___xor__(self):
        self.assertEqual(Empty[int]() ^ Empty[int](), FrozenIntervalSet[int]())
        self.assertEqual(
            Empty[int]() ^ Atomic[int].from_value(5),
            FrozenIntervalSet[int]([Atomic[int].from_value(5)]),
        )
        with self.assertRaises(TypeError):
            Empty[int]() ^ None

    def test___invert__(self):
        self.assertEqual(~Empty[int](), FrozenIntervalSet[int](~Empty[int]()))

    def test_meets(self):
        self.assertFalse(Empty[int]().meets(Interval[int]()))
        with self.assertRaises(TypeError):
            Empty[int]().meets(None)

    def test_overlaps(self):
        self.assertFalse(Empty[int]().overlaps(Interval[int]()))
        with self.assertRaises(TypeError):
            Empty[int]().overlaps(None)

    def test_starts(self):
        self.assertFalse(Empty[int]().starts(Interval[int]()))
        with self.assertRaises(TypeError):
            Empty[int]().starts(None)

    def test_during(self):
        self.assertFalse(Empty[int]().during(Interval[int]()))
        with self.assertRaises(TypeError):
            Empty[int]().during(None)

    def test_finishes(self):
        self.assertFalse(Empty[int]().finishes(Interval[int]()))
        with self.assertRaises(TypeError):
            Empty[int]().finishes(None)

    def test___str__(self):
        self.assertEqual(str(Empty[int]()), "")
