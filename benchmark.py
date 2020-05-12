# python benchmark.py -h

import argparse
import random
import time

from part import FrozenIntervalSet, FULL

parser = argparse.ArgumentParser(
    description="Benchmark of the intersection of sorted interval sets. "
    "Output the average number of output intervals, the average number of "
    "input intervals and the average time in seconds."
)
parser.add_argument("runs", metavar="#", type=int, help="number of runs")
parser.add_argument("count", metavar="N", type=int, help="number of lists")
parser.add_argument("length", metavar="K", type=int, help="number of unit intervals")
parser.add_argument("range", metavar="R", type=int, help="range unit intervals")
args = parser.parse_args()

count = 0
total = 0
interval_count = 0
for run in range(args.runs):
    lists = []
    for index in range(args.count):
        current = []
        for cursor in range(args.length):
            rand = random.randrange(args.range)
            current.append((rand, rand + 1))
        lists.append(FrozenIntervalSet(current))
        interval_count += len(lists[-1])
    start = time.time()
    count += len(FrozenIntervalSet([FULL]).intersection(*lists))
    end = time.time()
    total += end - start
print(
    f"{count / args.runs},"
    f"{interval_count / args.runs / args.count},"
    f"{total / args.runs}"
)
