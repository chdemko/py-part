import unittest

from part import Atomic, Empty, Interval, FrozenIntervalSet


class IntervalTestCase(unittest.TestCase):
    def test___init__(self):
        self.assertEqual(str(FrozenIntervalSet[int]()), "")
        self.assertEqual(str(FrozenIntervalSet[int]([Empty[int]()])), "")
        self.assertEqual(
            str(
                FrozenIntervalSet[int](
                    [
                        Interval[int](1, 2),
                        Interval[int](0, 1, upper_closed=True),
                    ]
                )
            ),
            "[0;2)",
        )
        self.assertEqual(
            str(FrozenIntervalSet[int]([Interval[int](2, 3), Interval[int](0, 1)])),
            "[0;1) | [2;3)",
        )
        self.assertEqual(str(FrozenIntervalSet[int]([(2, 3), (0, 1)])), "[0;1) | [2;3)")
        self.assertEqual(
            str(FrozenIntervalSet[int]([(2, 3), (0, 1), 1])), "[0;1] | [2;3)"
        )
        self.assertEqual(
            str(FrozenIntervalSet[int]([(2, 3), (0, 1, True, True)])),
            "[0;1] | [2;3)",
        )
        self.assertEqual(
            str(FrozenIntervalSet[int]([(2, 3, None), (0, 1)])), "[0;1) | (2;3)"
        )
        self.assertEqual(
            str(FrozenIntervalSet[int]([(2, 3), (0, 1, None)])), "(0;1) | [" "2;3)"
        )
        self.assertEqual(
            str(FrozenIntervalSet[int]([(2, 3), (0, 1), (1,)])), "[0;1] | [2;3)"
        )
        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 1, 2, 3, 4)])

    def test___hash__(self):
        self.assertEqual(
            hash(FrozenIntervalSet[int]([(2, 3), (0, 1), (1,)])),
            hash(FrozenIntervalSet[int]([(2, 3), (0, 1), (1,)])),
        )

    def test___eq__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(a, a)
        self.assertNotEqual(a, FrozenIntervalSet[int]())
        self.assertNotEqual(a, None)

    def test___le__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a <= FrozenIntervalSet[int]([(0, 30)]))
        self.assertTrue(a <= FrozenIntervalSet[int]([(0, 11), (12, 30)]))
        self.assertFalse(a <= FrozenIntervalSet[int]([(0, 9), (12, 30)]))
        self.assertTrue(a <= a)
        with self.assertRaises(TypeError):
            a <= None

    def test___lt__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a < FrozenIntervalSet[int]([(0, 30)]))
        self.assertTrue(a < FrozenIntervalSet[int]([(0, 11), (12, 30)]))
        self.assertFalse(a < FrozenIntervalSet[int]([(0, 9), (12, 30)]))
        self.assertFalse(a < a)
        with self.assertRaises(TypeError):
            a < None

    def test___ge__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(FrozenIntervalSet[int]([(0, 30)]) >= a)
        self.assertTrue(FrozenIntervalSet[int]([(0, 11), (12, 30)]) >= a)
        self.assertFalse(FrozenIntervalSet[int]([(0, 9), (12, 30)]) >= a)
        self.assertTrue(a >= a)
        with self.assertRaises(TypeError):
            a >= None

    def test___gt__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(FrozenIntervalSet[int]([(0, 30)]) > a)
        self.assertTrue(FrozenIntervalSet[int]([(0, 11), (12, 30)]) > a)
        self.assertFalse(FrozenIntervalSet[int]([(0, 9), (12, 30)]) > a)
        self.assertFalse(a > a)
        with self.assertRaises(TypeError):
            a > None

    def test___len__(self):
        self.assertEqual(len(FrozenIntervalSet[int]([(2, 3), (0, 1)])), 2)

    def test___bool__(self):
        self.assertTrue(FrozenIntervalSet[int]([(2, 3), (0, 1)]))
        self.assertFalse(FrozenIntervalSet[int]())

    def test___iter__(self):
        self.assertEqual(
            list(iter(FrozenIntervalSet[int]([(2, 3), (0, 1)]))),
            [Interval[int](0, 1), Interval[int](2, 3)],
        )

    def test___contains__(self):
        intervals = FrozenIntervalSet[int]([(2, 3), (0, 1)])
        self.assertIn(Interval[int](0, 1), intervals)
        self.assertIn(Interval[int](2, 3), intervals)
        self.assertNotIn(Interval[int](4, 5), intervals)
        self.assertNotIn(Interval[int](1, 2), intervals)
        self.assertNotIn(Interval[int](2, 3, upper_closed=True), intervals)
        self.assertIn(0, intervals)
        self.assertIn(Atomic[int].from_value(0), intervals)
        self.assertNotIn(Interval[int]("Hello", "World"), intervals)

    def test___getitem__(self):
        intervals = FrozenIntervalSet[int]([(2, 3), (0, 1)])
        self.assertEqual(intervals[0], Interval[int](0, 1))
        self.assertEqual(intervals[1], Interval[int](2, 3))
        self.assertEqual(intervals[1:], FrozenIntervalSet[int]([Interval[int](2, 3)]))
        with self.assertRaises(IndexError):
            intervals[2]

    def test___and__(self):
        self.assertEqual(
            str(
                FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
                & FrozenIntervalSet[int](
                    [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                )
            ),
            "[1;2) | [5;5] | [8;10) | [15;18) | [20;23) | [24;24]",
        )
        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]) & None

    def test___or__(self):
        self.assertEqual(
            str(
                FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
                | FrozenIntervalSet[int](
                    [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                )
            ),
            "[0;12) | [13;25)",
        )
        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]) | None

    def test___invert__(self):
        self.assertEqual(
            str(~FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])),
            "(-inf;0) | [2;5) | [10;13) | [23;24) | [25;+inf)",
        )
        self.assertEqual(str(~FrozenIntervalSet[int]()), "(-inf;+inf)")
        self.assertEqual(str(~~FrozenIntervalSet[int]()), "")
        self.assertEqual(str(~~~FrozenIntervalSet[int]()), "(-inf;+inf)")

    def test___sub__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a - FrozenIntervalSet[int]([(0, 6), (9, 12), (24, 30, None)])),
            "[6;9) | [13;23) | [24;24]",
        )
        with self.assertRaises(TypeError):
            a - None

    def test___xor__(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a ^ FrozenIntervalSet[int]([(0, 6), (9, 12), (24, 30, None)])),
            "[2;5) | [6;9) | [10;12) | [13;23) | [24;24] | [25;30)",
        )
        with self.assertRaises(TypeError):
            a ^ None

    def test_intersection(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(
                a.intersection(
                    FrozenIntervalSet[int](
                        [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                    ),
                    FrozenIntervalSet[int]([(1, 9), (16, 30)]),
                )
            ),
            "[1;2) | [5;5] | [8;9) | [16;18) | [20;23) | [24;24]",
        )
        self.assertEqual(str(a.intersection(FrozenIntervalSet[int]())), "")
        self.assertEqual(str(a.intersection(FrozenIntervalSet[int]([(-1, 0)]))), "")
        self.assertEqual(str(a.intersection(FrozenIntervalSet[int]([(1, 2)]))), "[1;2)")
        self.assertEqual(str(a.intersection(FrozenIntervalSet[int]([(11, 12)]))), "")
        self.assertEqual(
            str(a.intersection(FrozenIntervalSet[int]([(17, 24)]))), "[17;23)"
        )
        self.assertEqual(
            str(a.intersection(FrozenIntervalSet[int]([(24, 25)]))), "[24;25)"
        )
        self.assertEqual(str(a.intersection(FrozenIntervalSet[int]([(30, 31)]))), "")
        self.assertEqual(
            str(a.intersection([(6, 9)], [(6, 7), (8, 9)])), "[6;7) | [8;9)"
        )
        self.assertEqual(str(FrozenIntervalSet[int]().intersection()), "")

        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]).intersection(
                None
            )

        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]).intersection(
                1
            )

    def test_union(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(
                a.union(
                    FrozenIntervalSet[int](
                        [(1, 5, True, True), (8, 12), (15, 18), (20, 24, True, True)]
                    ),
                    FrozenIntervalSet[int]([(1, 9), (16, 30)]),
                )
            ),
            "[0;12) | [13;30)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]())),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]([(-1, 0)]))),
            "[-1;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]([(1, 2)]))),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]([(11, 12)]))),
            "[0;2) | [5;10) | [11;12) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]([(17, 24)]))),
            "[0;2) | [5;10) | [13;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]([(24, 25)]))),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(
            str(a.union(FrozenIntervalSet[int]([(30, 31)]))),
            "[0;2) | [5;10) | [13;23) | [24;25) | [30;31)",
        )
        self.assertEqual(
            str(a.union([(6, 9)], [(6, 7), (8, 9)])),
            "[0;2) | [5;10) | [13;23) | [24;25)",
        )
        self.assertEqual(str(FrozenIntervalSet[int]().union()), "")

        self.assertEqual(str(a.union([(2, 5)], [(10, 13), (23, 24)])), "[0;25)")

        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]).union(None)

        with self.assertRaises(TypeError):
            FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]).union(1)

    def test_isdisjoint(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a.isdisjoint(FrozenIntervalSet[int]()))
        self.assertTrue(a.isdisjoint(FrozenIntervalSet[int]([(-1, 0)])))
        self.assertFalse(a.isdisjoint(FrozenIntervalSet[int]([(1, 2)])))
        self.assertTrue(a.isdisjoint(FrozenIntervalSet[int]([(11, 12)])))
        self.assertFalse(a.isdisjoint(FrozenIntervalSet[int]([(17, 24)])))
        self.assertFalse(a.isdisjoint(FrozenIntervalSet[int]([(24, 25)])))
        self.assertTrue(a.isdisjoint(FrozenIntervalSet[int]([(30, 31)])))

    def test_issubset(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertTrue(a.issubset([(0, 30)]))
        self.assertTrue(a.issubset(FrozenIntervalSet[int]([(0, 30)])))
        self.assertTrue(a.issubset(FrozenIntervalSet[int]([(0, 11), (12, 30)])))
        self.assertFalse(a.issubset(FrozenIntervalSet[int]([(0, 9), (12, 30)])))
        self.assertTrue(a.issubset(a))

    def test_issuperset(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertFalse(a.issuperset([(0, 30)]))
        self.assertFalse(a.issuperset(FrozenIntervalSet[int]([(0, 30)])))
        self.assertFalse(a.issuperset(FrozenIntervalSet[int]([(0, 11), (12, 30)])))
        self.assertFalse(a.issuperset(FrozenIntervalSet[int]([(0, 9), (12, 30)])))
        self.assertTrue(a.issuperset(a))

    def test_difference(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(
                a.difference(FrozenIntervalSet[int]([(0, 6), (9, 12), (24, 30, None)]))
            ),
            "[6;9) | [13;23) | [24;24]",
        )

    def test_symmetric_difference(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(
            str(a.symmetric_difference([(0, 6), (9, 12), (24, 30, None)])),
            "[2;5) | [6;9) | [10;12) | [13;23) | [24;24] | [25;30)",
        )

    def test_copy(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(a, a.copy())
        self.assertNotEqual(id(a), id(a.copy()))

    def test_select(self):
        a = FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)])
        self.assertEqual(list(iter(a.select((1, 14)))), [Interval[int](5, 10)])
        self.assertEqual(
            list(iter(a.select((1, 14), strict=False))),
            [
                Interval[int](0, 2),
                Interval[int](5, 10),
                Interval[int](13, 23),
            ],
        )
        self.assertEqual(list(iter(a.select(Empty[int]()))), [])
        self.assertEqual(list(iter(a.select((24, 31, None)))), [])
        self.assertEqual(list(iter(a.select((30, 31)))), [])
        self.assertEqual(list(iter(a.select((-1, 1)))), [])
        self.assertEqual(list(iter(a.select((-1, 0)))), [])
        self.assertEqual(
            list(iter(a.select((24, 31, None), strict=False))),
            [Interval[int](24, 25)],
        )
        self.assertEqual(list(iter(a.select((30, 31), strict=False))), [])
        self.assertEqual(
            list(iter(a.select((-1, 1), strict=False))), [Interval[int](0, 2)]
        )
        self.assertEqual(list(iter(a.select((-1, 0), strict=False))), [])

    def test_reversed(self):
        self.assertEqual(
            list(reversed(FrozenIntervalSet[int]([(2, 3), (0, 1)]))),
            [Interval[int](2, 3), Interval[int](0, 1)],
        )
