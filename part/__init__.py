"""
The :mod:`part` package is designed to maintain subsets of sorted spaces.

It defines several classes.

For atomic values:

* :class:`TotallyOrdered` which represents totally ordered type;
* :class:`TO` which represents a generic totally ordered type;
* :class:`Atomic` which represents any convex subset of a totally ordered space;
* :class:`Empty` which represents the empty subset. There is only one instance of
  this class;
* :class:`Interval` which represents a non-empty subset of a totally ordered space.
  There is a special instance representing the whole space;

For set classes:

* :class:`IntervalSet` is an abstract class representing all interval sets;
* :class:`FrozenIntervalSet` is a frozen version of :class:`IntervalSet`;
* :class:`MutableIntervalSet` is a mutable version of :class:`IntervalSet`.

For dictionary classes:

* :class:`IntervalDict` is an abstract class representing all interval dictionaries;
* :class:`FrozenIntervalDict` is a frozen version of :class:`IntervalDict`;
* :class:`MutableIntervalDict` is a mutable version of :class:`IntervalDict`.

It also defines one constant:

* :const:`INFINITY` to hold the infinity value. (-:const:`INFINITY` is also a valid
  expression);
"""
from .atomic import Atomic, Empty, Interval, TO, TotallyOrdered
from .dicts import IntervalDict, FrozenIntervalDict, MutableIntervalDict
from .sets import IntervalSet, FrozenIntervalSet, MutableIntervalSet
from .values import INFINITY

__all__ = (
    "INFINITY",
    "TO",
    "TotallyOrdered",
    "Atomic",
    "Empty",
    "Interval",
    "IntervalSet",
    "FrozenIntervalSet",
    "MutableIntervalSet",
    "IntervalDict",
    "FrozenIntervalDict",
    "MutableIntervalDict",
)
