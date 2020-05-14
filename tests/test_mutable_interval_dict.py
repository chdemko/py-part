import unittest
import operator

from part import MutableIntervalDict, FrozenIntervalSet, Interval, Atomic


class MutableIntervalDictTestCase(unittest.TestCase):
    def test___item__(self):
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")
        with self.assertRaises(TypeError):
            _ = MutableIntervalDict[int, int](1)

    def test___setitem__(self):
        # Empty case
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})

        a[1:1] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:11] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        # From 1
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:7] = 1000
        self.assertEqual(
            str(a), "{'[1;7)': 1000, '[10;15)': 1, '[20;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:12] = 1000
        self.assertEqual(
            str(a), "{'[1;12)': 1000, '[12;15)': 1, '[20;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:17] = 1000
        self.assertEqual(str(a), "{'[1;17)': 1000, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:22] = 1000
        self.assertEqual(str(a), "{'[1;22)': 1000, '[22;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:27] = 1000
        self.assertEqual(str(a), "{'[1;27)': 1000, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:32] = 1000
        self.assertEqual(str(a), "{'[1;32)': 1000, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[1:42] = 1000
        self.assertEqual(str(a), "{'[1;42)': 1000}")

        # From 11
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:12] = 1000
        self.assertEqual(
            str(a),
            "{'[10;11)': 1, '[11;12)': 1000, '[12;15)': 1, '[20;25)': 2, '[30;35)': 3}",
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:17] = 1000
        self.assertEqual(
            str(a), "{'[10;11)': 1, '[11;17)': 1000, '[20;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:22] = 1000
        self.assertEqual(
            str(a), "{'[10;11)': 1, '[11;22)': 1000, '[22;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:27] = 1000
        self.assertEqual(str(a), "{'[10;11)': 1, '[11;27)': 1000, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:32] = 1000
        self.assertEqual(str(a), "{'[10;11)': 1, '[11;32)': 1000, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[11:42] = 1000
        self.assertEqual(str(a), "{'[10;11)': 1, '[11;42)': 1000}")

        # From 16
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[16:17] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[16;17)': 1000, '[20;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[16:22] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[16;22)': 1000, '[22;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[16:27] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[16;27)': 1000, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[16:32] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[16;32)': 1000, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[16:42] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[16;42)': 1000}")

        # From 21
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[21:22] = 1000
        self.assertEqual(
            str(a),
            "{'[10;15)': 1, '[20;21)': 2, '[21;22)': 1000, '[22;25)': 2, '[30;35)': 3}",
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[21:27] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;21)': 2, '[21;27)': 1000, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[21:32] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;21)': 2, '[21;32)': 1000, '[32;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[21:42] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;21)': 2, '[21;42)': 1000}")

        # From 26
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[26:27] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;25)': 2, '[26;27)': 1000, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[26:32] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;25)': 2, '[26;32)': 1000, '[32;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[26:42] = 1000
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[26;42)': 1000}")

        # From 31
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[31:32] = 1000
        self.assertEqual(
            str(a),
            "{'[10;15)': 1, '[20;25)': 2, '[30;31)': 3, '[31;32)': 1000, '[32;35)': 3}",
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[31:42] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;31)': 3, '[31;42)': 1000}"
        )

        # From 36
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[36:42] = 1000
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3, '[36;42)': 1000}"
        )

    def test___delitem__(self):
        # Empty case
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:1]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:11]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        # From 1
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:7]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:12]
        self.assertEqual(str(a), "{'[12;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:17]
        self.assertEqual(str(a), "{'[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:22]
        self.assertEqual(str(a), "{'[22;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:27]
        self.assertEqual(str(a), "{'[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:32]
        self.assertEqual(str(a), "{'[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[1:42]
        self.assertEqual(str(a), "{}")

        # From 11
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:12]
        self.assertEqual(
            str(a), "{'[10;11)': 1, '[12;15)': 1, '[20;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:17]
        self.assertEqual(str(a), "{'[10;11)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:22]
        self.assertEqual(str(a), "{'[10;11)': 1, '[22;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:27]
        self.assertEqual(str(a), "{'[10;11)': 1, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:32]
        self.assertEqual(str(a), "{'[10;11)': 1, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[11:42]
        self.assertEqual(str(a), "{'[10;11)': 1}")

        # From 16
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[16:17]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[16:22]
        self.assertEqual(str(a), "{'[10;15)': 1, '[22;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[16:27]
        self.assertEqual(str(a), "{'[10;15)': 1, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[16:32]
        self.assertEqual(str(a), "{'[10;15)': 1, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[16:42]
        self.assertEqual(str(a), "{'[10;15)': 1}")

        # From 21
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[21:22]
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;21)': 2, '[22;25)': 2, '[30;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[21:27]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;21)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[21:32]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;21)': 2, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[21:42]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;21)': 2}")

        # From 26
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[26:27]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[26:32]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[32;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[26:42]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2}")

        # From 31
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[31:32]
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;31)': 3, '[32;35)': 3}"
        )

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[31:42]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;31)': 3}")

        # From 36
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        del a[36:42]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a[12] = 4
        a[14:22] = 5
        del a[12:22]
        self.assertEqual(str(a), "{'[10;12)': 1, '[22;25)': 2, '[30;35)': 3}")

        # Test self._stop when interval is empty
        a = MutableIntervalDict[int, int](
            {(10, 15): 1, (20, 25): 2, (30, 35, True, True): 3}
        )
        del a[11:35]
        self.assertEqual(str(a), "{'[10;11)': 1, '[35;35]': 3}")
        a = MutableIntervalDict[int, int](
            {(10, 15): 1, (20, 25): 2, (30, 35, True, True): 3}
        )
        del a[21:35]
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;21)': 2, '[35;35]': 3}")
        a = MutableIntervalDict[int, int](
            {(10, 15): 1, (20, 25): 2, (30, 35, True, True): 3}
        )
        del a[31:35]
        self.assertEqual(
            str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;31)': 3, '[35;35]': 3}"
        )

    def test_pop(self):
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(a.pop((10, 13)), 1)
        self.assertEqual(str(a), "{'[13;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(a.pop((13, 16), 2), 2)
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        with self.assertRaises(KeyError):
            a.pop((13, 16))

    def test_popitem(self):
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(a.popitem(), (Atomic.from_tuple((10, 15)), 1))

    def test_setdefault(self):
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(a.setdefault((10, 15), 2), 1)
        self.assertEqual(a.setdefault((13, 17), 2), 2)
        self.assertEqual(
            str(a), "{'[10;13)': 1, '[13;17)': 2, '[20;25)': 2, '[30;35)': 3}"
        )

    def test_clear(self):
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a.clear()
        self.assertEqual(str(a), "{}")

    def test_default(self):
        a = MutableIntervalDict[int, int](
            {(10, 15): 1, (20, 25): 2, (30, 35): 3}, default=set
        )
        self.assertEqual(a[(13, 16)], set())
        self.assertEqual(
            str(a), "{'[10;13)': 1, '[13;16)': set(), '[20;25)': 2, '[30;35)': 3}"
        )

    def test_compress(self):
        a = MutableIntervalDict[int, int](default=set)
        interval = Interval(1, 10)
        value = 1
        intervals = FrozenIntervalSet(a.select(interval, strict=False))
        for other in ((interval & found)[0] for found in intervals):
            a[other] = a[other].copy()
            a[other].add(value)
        for other in FrozenIntervalSet([interval]) - intervals:
            a[other].add(value)
        self.assertEqual(str(a), "{'[1;10)': {1}}")

        interval = Interval(5, 20)
        value = 2
        intervals = FrozenIntervalSet(a.select(interval, strict=False))
        for other in ((interval & found)[0] for found in intervals):
            a[other] = a[other].copy()
            a[other].add(value)
        for other in FrozenIntervalSet([interval]) - intervals:
            a[other].add(value)
        self.assertEqual(str(a), "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2}}")

        interval = Interval(10, 30)
        value = 1
        intervals = FrozenIntervalSet(a.select(interval, strict=False))
        for other in ((interval & found)[0] for found in intervals):
            a[other] = a[other].copy()
            a[other].add(value)
        for other in FrozenIntervalSet([interval]) - intervals:
            a[other].add(value)
        self.assertEqual(
            str(a),
            "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {1, 2}, '[20;30)': {1}}",
        )
        self.assertEqual(
            str(a.compress()), "{'[1;5)': {1}, '[5;20)': {1, 2}, '[20;30)': {1}}"
        )

    def test_update(self):
        a = MutableIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        a.update([((13, 16), 4), ((40, 45), 5)])
        self.assertEqual(
            str(a),
            "{'[10;13)': 1, '[13;16)': 4, '[20;25)': 2, '[30;35)': 3, '[40;45)': 5}",
        )
        a = MutableIntervalDict[int, int](default=set, update=lambda x, y: x.copy() | y)
        a.update({(1, 10): {1}})
        self.assertEqual(str(a), "{'[1;10)': {1}}")
        a.update({(5, 20): {2}})
        self.assertEqual(str(a), "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2}}")
        a.update({(10, 30): {1}})
        self.assertEqual(
            str(a),
            "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {1, 2}, '[20;30)': {1}}",
        )
        a = MutableIntervalDict[int, int](default=set)
        a.update({(1, 10): {1}}, function=lambda x, y: x.copy() | y)
        self.assertEqual(str(a), "{'[1;10)': {1}}")
        a.update({(5, 20): {2}}, function=lambda x, y: x.copy() | y)
        self.assertEqual(str(a), "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2}}")

    def test___or__(self):
        a = MutableIntervalDict[int, int](
            {(10, 15): 1, (20, 25): 2, (30, 35): 3}, update=operator.add
        )
        self.assertEqual(
            str(a | MutableIntervalDict[int, int]({(15, 22): 4})),
            "{'[10;15)': 1, '[15;20)': 4, '[20;22)': 6, '[22;25)': 2, '[30;35)': 3}",
        )
        with self.assertRaises(TypeError):
            a | None

    def test___ior__(self):
        a = MutableIntervalDict[int, int](update=lambda x, y: x.copy() | y)
        a |= MutableIntervalDict[int, int]({(1, 10): {1}})
        self.assertEqual(str(a), "{'[1;10)': {1}}")
        a |= MutableIntervalDict[int, int]({(5, 20): {2}})
        self.assertEqual(str(a), "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2}}")
        a |= MutableIntervalDict[int, int]({(10, 30): {1}})
        self.assertEqual(
            str(a),
            "{'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {1, 2}, '[20;30)': {1}}",
        )
        a |= MutableIntervalDict[int, int]({(7, 25): {3}})
        self.assertEqual(
            str(a),
            "{'[1;5)': {1}, '[5;7)': {1, 2}, '[7;10)': {1, 2, 3}, '[10;20)': {1, 2, 3}, '[20;25)': {1, 3}, '[25;30)': {1}}",
        )
        with self.assertRaises(TypeError):
            a |= None


if __name__ == "__main__":
    unittest.main()
