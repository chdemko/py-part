"""
The :mod:`part` package is designed to maintain subsets of sorted spaces and defines
several classes:

* :class:`Atomic` which represents any convex subset of a totally ordered space;
* :class:`Empty` which represents the empty subset. There is only one instance of
  this class called :const:`EMPTY <Empty>`;
* :class:`Interval` which represents a non-empty subset of a totally ordered space.
  There is a special instance representing the whole space called
  :const:`FULL <Interval>`;
* :class:`IntervalSet` is an abstract class representing all interval sets;
* :class:`FrozenIntervalSet` is a frozen version of :class:`IntervalSet`;
* :class:`MutableIntervalSet` is a mutable version of :class:`IntervalSet`.

It also defines two constants:

* :const:`INFINITY` to hold the infinity value. (-:const:`INFINITY` is also a valid
  expression);
* :const:`EMPTY <Empty>` to hold the empty subset.
* :const:`FULL <Interval>` to hold the full set.
"""
from .atomic import Atomic, Empty, EMPTY, Interval, FULL
from .sets import IntervalSet, FrozenIntervalSet, MutableIntervalSet
from .values import INFINITY
from .dicts import IntervalDict, FrozenIntervalDict, MutableIntervalDict

__all__ = (
    "INFINITY",
    "Atomic",
    "Empty",
    "EMPTY",
    "Interval",
    "FULL",
    "IntervalSet",
    "FrozenIntervalSet",
    "MutableIntervalSet",
    "IntervalDict",
    "FrozenIntervalDict",
    "MutableIntervalDict",
)
