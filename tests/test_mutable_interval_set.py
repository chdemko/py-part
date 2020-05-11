import unittest

from part import Interval, MutableIntervalSet, EMPTY


class IntervalTestCase(unittest.TestCase):
    def test___contains__(self):
        self.assertIn(
            Interval(0, 2), MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        )
        self.assertNotIn(
            Interval(1, 2), MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        )

    def test___getitem(self):
        intervals = MutableIntervalSet([(2, 3), (0, 1)])
        self.assertEqual(intervals[1:], MutableIntervalSet([Interval(2, 3)]))

    def test_add(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.add(Interval(lower_value=1, upper_value=3))
        self.assertEqual(str(a), "[0;3) | [5;10) | [13;23) | [24;25)")
        a.add(EMPTY)
        self.assertEqual(str(a), "[0;3) | [5;10) | [13;23) | [24;25)")

    def test_remove(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.remove(Interval(lower_value=1, upper_value=2))
        self.assertEqual(str(a), "[0;1) | [5;10) | [13;23) | [24;25)")
        a.remove(EMPTY)
        self.assertEqual(str(a), "[0;1) | [5;10) | [13;23) | [24;25)")
        with self.assertRaises(KeyError):
            a.remove(Interval(lower_value=1, upper_value=1, upper_closed=True))
        with self.assertRaises(KeyError):
            a.remove(Interval(lower_value=0, upper_value=1, upper_closed=True))
        with self.assertRaises(KeyError):
            a.remove(Interval(lower_value=0, upper_value=6, upper_closed=True))
        with self.assertRaises(KeyError):
            a.remove(Interval(lower_value=2, upper_value=6, upper_closed=True))
        with self.assertRaises(KeyError):
            a.remove(Interval(lower_value=2, upper_value=12, upper_closed=True))

    def test_discard(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.discard(Interval(lower_value=1, upper_value=14))
        self.assertEqual(str(a), "[0;1) | [14;23) | [24;25)")
        a.discard(Interval(lower_value=15, upper_value=16))
        self.assertEqual(str(a), "[0;1) | [14;15) | [16;23) | [24;25)")
        a.discard((16, 17))
        self.assertEqual(str(a), "[0;1) | [14;15) | [17;23) | [24;25)")
        a.discard(20)
        self.assertEqual(str(a), "[0;1) | [14;15) | [17;20) | (20;23) | [24;25)")
        a.discard(EMPTY)
        self.assertEqual(str(a), "[0;1) | [14;15) | [17;20) | (20;23) | [24;25)")

    def test___ior__(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a |= MutableIntervalSet([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[0;2) | [5;10) | [13;23) | [24;30) | [31;34)")
        with self.assertRaises(TypeError):
            a |= None

    def test_update(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.update([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[0;2) | [5;10) | [13;23) | [24;30) | [31;34)")

    def test___iand__(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a &= MutableIntervalSet([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[24;25)")
        with self.assertRaises(TypeError):
            a &= None

    def test_intersection_update(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.intersection_update([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[24;25)")

    def test___isub__(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a -= MutableIntervalSet([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[0;2) | [5;10) | [13;23)")
        with self.assertRaises(TypeError):
            a -= None

    def test_difference_update(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.difference_update([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[0;2) | [5;10) | [13;23)")

    def test___ixor__(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a ^= MutableIntervalSet([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[0;2) | [5;10) | [13;23) | [25;30) | [31;34)")
        with self.assertRaises(TypeError):
            a ^= None

    def test_symmetric_difference_update(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.symmetric_difference_update([(24, 30), (31, 34)])
        self.assertEqual(str(a), "[0;2) | [5;10) | [13;23) | [25;30) | [31;34)")

    def test_pop(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(a.pop(), Interval.from_tuple((0, 2)))
        self.assertEqual(str(a), "[5;10) | [13;23) | [24;25)")
        with self.assertRaises(KeyError):
            MutableIntervalSet().pop()

    def test_clear(self):
        a = MutableIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        a.clear()
        self.assertEqual(str(a), "")
