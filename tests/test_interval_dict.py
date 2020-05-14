import unittest

from part import FrozenIntervalDict, Empty


class IntervalDictTestCase(unittest.TestCase):
    def test___init__(self):
        a = FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")
        a = FrozenIntervalDict[int, int](
            {(10, 15): 1, (14, 25): 1, (30, 35): 2, (33, 45): 2}
        )
        self.assertEqual(
            str(a), "{'[10;14)': 1, '[14;25)': 1, '[30;33)': 2, '[33;45)': 2}"
        )

    def test___hash__(self):
        self.assertEqual(
            hash(FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})),
            hash(FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})),
        )

    def test___iter__(self):
        self.assertEqual(
            list(
                str(interval)
                for interval in FrozenIntervalDict[int, int](
                    {(10, 15): 1, (20, 25): 2, (30, 35): 3}
                )
            ),
            ["[10;15)", "[20;25)", "[30;35)"],
        )

    def test___contains__(self):
        a = FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertTrue((10, 15) in a)
        self.assertFalse((10, 18) in a)
        self.assertTrue((11, 14) in a)
        self.assertFalse((40, 45) in a)
        self.assertTrue(Empty[int]() in a)

    def test___getitem__(self):
        a = FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(a[(11, 14)], 1)
        self.assertEqual(str(a[12:32]), "{'[12;15)': 1, '[20;25)': 2, '[30;32)': 3}")
        self.assertEqual(str(a), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")
        with self.assertRaises(KeyError):
            _ = a[(11, 16)]
        with self.assertRaises(ValueError):
            _ = a[11:16:1]

    def test___or__(self):
        a = FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        self.assertEqual(
            str(a | FrozenIntervalDict[int, int]({(15, 22): 4})),
            "{'[10;15)': 1, '[15;22)': 4, '[22;25)': 2, '[30;35)': 3}",
        )
        with self.assertRaises(TypeError):
            a | None

    def test_copy(self):
        a = FrozenIntervalDict[int, int]({(10, 15): 1, (20, 25): 2, (30, 35): 3})
        b = a.copy()
        self.assertEqual(str(b), "{'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}")

    def test_select(self):
        a = FrozenIntervalDict[int, int](
            {(10, 15): 1, (20, 25): 2, (30, 35): 3, (40, 45): 3}
        )
        self.assertEqual(
            [str(interval) for interval in a.select((22, 42))], ["[30;35)"]
        )
        self.assertEqual(
            [str(interval) for interval in a.select((22, 37))], ["[30;35)"]
        )
        self.assertEqual(
            [str(interval) for interval in a.select((22, 42), strict=False)],
            ["[20;25)", "[30;35)", "[40;45)"],
        )
        self.assertEqual([str(interval) for interval in a.select(Empty[int]())], [])

    def test_compress(self):
        a = FrozenIntervalDict[int, int](
            {(10, 15): 1, (14, 25): 1, (30, 35): 2, (33, 45): 2}
        )
        b = a.compress()
        self.assertEqual(str(b), "{'[10;25)': 1, '[30;45)': 2}")


if __name__ == "__main__":
    unittest.main()
