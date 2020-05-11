import unittest

from part import Atomic, Interval, EMPTY, FrozenIntervalSet


class IntervalTestCase(unittest.TestCase):
    def test___init__(self):
        self.assertEqual(str(FrozenIntervalSet()), "")
        self.assertEqual(str(FrozenIntervalSet([EMPTY])), "")
        self.assertEqual(
            str(FrozenIntervalSet([Interval(1, 2), Interval(0, 1, upper_closed=True)])),
            "[0;2)",
        )
        self.assertEqual(
            str(FrozenIntervalSet([Interval(2, 3), Interval(0, 1)])), "[0;1) | [2;3)"
        )
        self.assertEqual(str(FrozenIntervalSet([(2, 3), (0, 1)])), "[0;1) | [2;3)")
        self.assertEqual(str(FrozenIntervalSet([(2, 3), (0, 1), 1])), "[0;1] | [2;3)")
        self.assertEqual(
            str(FrozenIntervalSet([(2, 3), (0, 1, True, True)])), "[0;1] | [2;3)"
        )
        self.assertEqual(
            str(FrozenIntervalSet([(2, 3, None), (0, 1)])), "[0;1) | (2;3)"
        )
        self.assertEqual(
            str(FrozenIntervalSet([(2, 3), (0, 1, None)])), "(0;1) | [" "2;3)"
        )
        self.assertEqual(
            str(FrozenIntervalSet([(2, 3), (0, 1), (1,)])), "[0;1] | [2;3)"
        )
        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 1, 2, 3, 4)])

    def test___hash__(self):
        self.assertEqual(
            hash(FrozenIntervalSet([(2, 3), (0, 1), (1,)])),
            hash(FrozenIntervalSet([(2, 3), (0, 1), (1,)])),
        )

    def test___eq__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(a, a)
        self.assertNotEqual(a, FrozenIntervalSet())
        self.assertNotEqual(a, None)

    def test___le__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a <= FrozenIntervalSet([(0, 30)]))
        self.assertTrue(a <= FrozenIntervalSet([(0, 11), (12, 30)]))
        self.assertFalse(a <= FrozenIntervalSet([(0, 9), (12, 30)]))
        self.assertTrue(a <= a)
        with self.assertRaises(TypeError):
            a <= None

    def test___lt__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a < FrozenIntervalSet([(0, 30)]))
        self.assertTrue(a < FrozenIntervalSet([(0, 11), (12, 30)]))
        self.assertFalse(a < FrozenIntervalSet([(0, 9), (12, 30)]))
        self.assertFalse(a < a)
        with self.assertRaises(TypeError):
            a < None

    def test___ge__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(FrozenIntervalSet([(0, 30)]) >= a)
        self.assertTrue(FrozenIntervalSet([(0, 11), (12, 30)]) >= a)
        self.assertFalse(FrozenIntervalSet([(0, 9), (12, 30)]) >= a)
        self.assertTrue(a >= a)
        with self.assertRaises(TypeError):
            a >= None

    def test___gt__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(FrozenIntervalSet([(0, 30)]) > a)
        self.assertTrue(FrozenIntervalSet([(0, 11), (12, 30)]) > a)
        self.assertFalse(FrozenIntervalSet([(0, 9), (12, 30)]) > a)
        self.assertFalse(a > a)
        with self.assertRaises(TypeError):
            a > None

    def test___len__(self):
        self.assertEqual(len(FrozenIntervalSet([(2, 3), (0, 1)])), 2)

    def test___bool__(self):
        self.assertTrue(FrozenIntervalSet([(2, 3), (0, 1)]))
        self.assertFalse(FrozenIntervalSet())

    def test___iter__(self):
        self.assertEqual(
            list(iter(FrozenIntervalSet([(2, 3), (0, 1)]))),
            [Interval(0, 1), Interval(2, 3)],
        )

    def test___contains__(self):
        intervals = FrozenIntervalSet([(2, 3), (0, 1)])
        self.assertIn(Interval(0, 1), intervals)
        self.assertIn(Interval(2, 3), intervals)
        self.assertNotIn(Interval(4, 5), intervals)
        self.assertNotIn(Interval(1, 2), intervals)
        self.assertNotIn(Interval(2, 3, upper_closed=True), intervals)
        self.assertIn(0, intervals)
        self.assertIn(Atomic.from_value(0), intervals)
        self.assertNotIn(Interval("Hello", "World"), intervals)

    def test___getitem__(self):
        intervals = FrozenIntervalSet([(2, 3), (0, 1)])
        self.assertEqual(intervals[0], Interval(0, 1))
        self.assertEqual(intervals[1], Interval(2, 3))
        self.assertEqual(intervals[1:], FrozenIntervalSet([Interval(2, 3)]))
        with self.assertRaises(IndexError):
            intervals[2]

    def test___and__(self):
        self.assertEqual(
            str(
                FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
                & FrozenIntervalSet(
                    [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                )
            ),
            "[1;2) | [5;5] | [8;10) | [15;18) | [20;23) | [24;24]",
        )
        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)]) & None

    def test___or__(self):
        self.assertEqual(
            str(
                FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
                | FrozenIntervalSet(
                    [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                )
            ),
            "[0;12) | [13;25)",
        )
        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)]) | None

    def test___invert__(self):
        self.assertEqual(
            str(~FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])),
            "(-inf;0) | [2;5) | [10;13) | [23;24) | [25;+inf)",
        )
        self.assertEqual(str(~FrozenIntervalSet()), "(-inf;+inf)")
        self.assertEqual(str(~~FrozenIntervalSet()), "")
        self.assertEqual(str(~~~FrozenIntervalSet()), "(-inf;+inf)")

    def test___sub__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a - FrozenIntervalSet([(0, 6), (9, 12), (24, 30, None)])),
            "[6;9) | [13;23) | [24;24]",
        )
        with self.assertRaises(TypeError):
            a - None

    def test___xor__(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a ^ FrozenIntervalSet([(0, 6), (9, 12), (24, 30, None)])),
            "[2;5) | [6;9) | [10;12) | [13;23) | [24;24] | [25;30)",
        )
        with self.assertRaises(TypeError):
            a ^ None

    def test_intersection(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(
                a.intersection(
                    FrozenIntervalSet(
                        [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                    ),
                    FrozenIntervalSet([(1, 9), (16, 30)]),
                )
            ),
            "[1;2) | [5;5] | [8;9) | [16;18) | [20;23) | [24;24]",
        )
        self.assertEqual(str(a.intersection(FrozenIntervalSet())), "")
        self.assertEqual(str(a.intersection(FrozenIntervalSet([(-1, 0)]))), "")
        self.assertEqual(str(a.intersection(FrozenIntervalSet([(1, 2)]))), "[1;2)")
        self.assertEqual(str(a.intersection(FrozenIntervalSet([(11, 12)]))), "")
        self.assertEqual(str(a.intersection(FrozenIntervalSet([(17, 24)]))), "[17;23)")
        self.assertEqual(str(a.intersection(FrozenIntervalSet([(24, 25)]))), "[24;25)")
        self.assertEqual(str(a.intersection(FrozenIntervalSet([(30, 31)]))), "")
        self.assertEqual(
            str(a.intersection([(6, 9)], [(6, 7), (8, 9)])), "[6;7) | [8;9)"
        )
        self.assertEqual(str(FrozenIntervalSet().intersection()), "")

        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)]).intersection(None)

        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)]).intersection(1)

    def test_union(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(
                a.union(
                    FrozenIntervalSet(
                        [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                    ),
                    FrozenIntervalSet([(1, 9), (16, 30)]),
                )
            ),
            "[0;12) | [13;30)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet())), "[0;2) | [5;10) | [13;23) | [24;25)"
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet([(-1, 0)]))),
            "[-1;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet([(1, 2)]))),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet([(11, 12)]))),
            "[0;2) | [5;10) | [11;12) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet([(17, 24)]))), "[0;2) | [5;10) | [13;25)"
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet([(24, 25)]))),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet([(30, 31)]))),
            "[0;2) | [5;10) | [13;23) | [24;25) | [30;31)",
        )
        self.assertEqual(
            str(a.union([(6, 9)], [(6, 7), (8, 9)])),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(str(FrozenIntervalSet().union()), "")

        self.assertEqual(str(a.union([(2, 5)], [(10, 13), (23, 24)])), "[0;25)")

        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)]).union(None)

        with self.assertRaises(TypeError):
            FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)]).union(1)

    def test_isdisjoint(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a.isdisjoint(FrozenIntervalSet()))
        self.assertTrue(a.isdisjoint(FrozenIntervalSet([(-1, 0)])))
        self.assertFalse(a.isdisjoint(FrozenIntervalSet([(1, 2)])))
        self.assertTrue(a.isdisjoint(FrozenIntervalSet([(11, 12)])))
        self.assertFalse(a.isdisjoint(FrozenIntervalSet([(17, 24)])))
        self.assertFalse(a.isdisjoint(FrozenIntervalSet([(24, 25)])))
        self.assertTrue(a.isdisjoint(FrozenIntervalSet([(30, 31)])))

    def test_issubset(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a.issubset([(0, 30)]))
        self.assertTrue(a.issubset(FrozenIntervalSet([(0, 30)])))
        self.assertTrue(a.issubset(FrozenIntervalSet([(0, 11), (12, 30)])))
        self.assertFalse(a.issubset(FrozenIntervalSet([(0, 9), (12, 30)])))
        self.assertTrue(a.issubset(a))

    def test_issuperset(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertFalse(a.issuperset([(0, 30)]))
        self.assertFalse(a.issuperset(FrozenIntervalSet([(0, 30)])))
        self.assertFalse(a.issuperset(FrozenIntervalSet([(0, 11), (12, 30)])))
        self.assertFalse(a.issuperset(FrozenIntervalSet([(0, 9), (12, 30)])))
        self.assertTrue(a.issuperset(a))

    def test_difference(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a.difference(FrozenIntervalSet([(0, 6), (9, 12), (24, 30, None)]))),
            "[6;9) | [13;23) | [24;24]",
        )

    def test_symmetric_difference(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a.symmetric_difference([(0, 6), (9, 12), (24, 30, None)])),
            "[2;5) | [6;9) | [10;12) | [13;23) | [24;24] | [25;30)",
        )

    def test_copy(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(a, a.copy())
        self.assertNotEqual(id(a), id(a.copy()))

    def test_select(self):
        a = FrozenIntervalSet([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(list(iter(a.select((1, 14)))), [Interval(5, 10)])
        self.assertEqual(
            list(iter(a.select((1, 14), strict=False))),
            [Interval(0, 2), Interval(5, 10), Interval(13, 23)],
        )
        self.assertEqual(list(iter(a.select(EMPTY))), [])
        self.assertEqual(list(iter(a.select((24, 31, None)))), [])
        self.assertEqual(list(iter(a.select((30, 31)))), [])
        self.assertEqual(list(iter(a.select((-1, 1)))), [])
        self.assertEqual(list(iter(a.select((-1, 0)))), [])
        self.assertEqual(
            list(iter(a.select((24, 31, None), strict=False))), [Interval(24, 25)]
        )
        self.assertEqual(list(iter(a.select((30, 31), strict=False))), [])
        self.assertEqual(list(iter(a.select((-1, 1), strict=False))), [Interval(0, 2)])
        self.assertEqual(list(iter(a.select((-1, 0), strict=False))), [])

    def test_reversed(self):
        self.assertEqual(
            list(reversed(FrozenIntervalSet([(2, 3), (0, 1)]))),
            [Interval(2, 3), Interval(0, 1)],
        )
