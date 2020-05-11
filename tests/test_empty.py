import unittest

from part import EMPTY, Interval, FrozenIntervalSet, Atomic
from part import FULL


class IntervalTestCase(unittest.TestCase):
    def test___bool__(self):
        self.assertFalse(bool(EMPTY))

    def test___hash__(self):
        self.assertEqual(hash(EMPTY), id(EMPTY))

    def test___eq__(self):
        self.assertEqual(EMPTY, EMPTY)
        self.assertNotEqual(EMPTY, None)

    def test___lt__(self):
        self.assertFalse(EMPTY < EMPTY)
        self.assertFalse(EMPTY < Interval())
        with self.assertRaises(TypeError):
            EMPTY < None

    def test___gt__(self):
        self.assertFalse(EMPTY > EMPTY)
        self.assertFalse(EMPTY > Interval())
        with self.assertRaises(TypeError):
            EMPTY > None

    def test___or__(self):
        self.assertEqual(EMPTY | EMPTY, FrozenIntervalSet())
        self.assertEqual(EMPTY | Atomic.from_value(5), FrozenIntervalSet([5]))
        with self.assertRaises(TypeError):
            EMPTY | None

    def test___and__(self):
        self.assertEqual(EMPTY & EMPTY, FrozenIntervalSet())
        self.assertEqual(EMPTY & Atomic.from_value(5), FrozenIntervalSet())
        with self.assertRaises(TypeError):
            EMPTY & None

    def test___sub__(self):
        self.assertEqual(EMPTY - EMPTY, FrozenIntervalSet())
        self.assertEqual(EMPTY - Atomic.from_value(5), FrozenIntervalSet())
        with self.assertRaises(TypeError):
            EMPTY - None

    def test___xor__(self):
        self.assertEqual(EMPTY ^ EMPTY, FrozenIntervalSet())
        self.assertEqual(
            EMPTY ^ Atomic.from_value(5), FrozenIntervalSet([Atomic.from_value(5)])
        )
        with self.assertRaises(TypeError):
            EMPTY ^ None

    def test___invert__(self):
        self.assertEqual(~EMPTY, FrozenIntervalSet([FULL]))

    def test_meets(self):
        self.assertFalse(EMPTY.meets(Interval()))
        with self.assertRaises(TypeError):
            EMPTY.meets(None)

    def test_overlaps(self):
        self.assertFalse(EMPTY.overlaps(Interval()))
        with self.assertRaises(TypeError):
            EMPTY.overlaps(None)

    def test_starts(self):
        self.assertFalse(EMPTY.starts(Interval()))
        with self.assertRaises(TypeError):
            EMPTY.starts(None)

    def test_during(self):
        self.assertFalse(EMPTY.during(Interval()))
        with self.assertRaises(TypeError):
            EMPTY.during(None)

    def test_finishes(self):
        self.assertFalse(EMPTY.finishes(Interval()))
        with self.assertRaises(TypeError):
            EMPTY.finishes(None)

    def test___str__(self):
        self.assertEqual(str(EMPTY), "")
