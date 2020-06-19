"""
Compute a benchmark of MutableIntervalDict update.
"""

# python benchmark_dicts.py -h

import argparse
import operator
import random
import time

from part import MutableIntervalDict

# pylint: disable=invalid-name

parser = argparse.ArgumentParser(
    description="Benchmark of the update of sorted interval dicts. "
    "Output the average number of output intervals, the average number of "
    "input intervals and the average time in seconds."
)
parser.add_argument("runs", metavar="#", type=int, help="number of runs")
parser.add_argument("count", metavar="N", type=int, help="number of dicts")
parser.add_argument("length", metavar="K", type=int, help="number of unit intervals")
parser.add_argument("range", metavar="R", type=int, help="range unit intervals")
args = parser.parse_args()

count = 0
total1 = 0
total2 = 0
interval_count = 0
for run in range(args.runs):
    dicts = []
    for index in range(args.count):
        current = []
        for cursor in range(args.length):
            rand = random.randrange(args.range)
            current.append(((rand, rand + 1), 1))
        dicts.append(MutableIntervalDict[int, int](current))
        interval_count += len(dicts[-1])

    start1 = time.time()
    result = MutableIntervalDict[int, int](operator=operator.add, strict=False)
    result.update(*dicts)
    count += len(result)
    end1 = time.time()
    total1 += end1 - start1

    start2 = time.time()
    result = MutableIntervalDict[int, int](operator=operator.add, strict=True)
    result.update(*dicts)
    count += len(result)
    end2 = time.time()
    total2 += end2 - start2
print(
    f"{count / args.runs},"
    f"{interval_count / args.runs / args.count},"
    f"{total1 / args.runs}"
)
print(
    f"{count / args.runs},"
    f"{interval_count / args.runs / args.count},"
    f"{total2 / args.runs}"
)
