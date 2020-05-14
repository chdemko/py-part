"""Interval sets module."""

# pylint: disable=too-many-lines

import bisect
import copy
import heapq
from abc import abstractmethod, ABCMeta
from typing import (
    Optional,
    Iterable,
    Iterator,
    List,
    Generic,
    AbstractSet,
    MutableSet,
    Union,
)

# pylint: disable=too-few-public-methods,import-error
from sortedcontainers import SortedSet  # type: ignore

from part import atomic, values


class IntervalSet(
    Generic[atomic.TO], AbstractSet[atomic.Interval[atomic.TO]], metaclass=ABCMeta
):
    """
    Interval Set class.

    The :class:`IntervalSet` abstract class is designed to hold disjoint sorted
    intervals. It implements the :class:`AbstractSet <python:typing.AbstractSet>`
    protocol. It is implemented in two concrete classes:

    * :class:`FrozenIntervalSet`
    * :class:`MutableIntervalSet`
    """

    __slots__ = ("_intervals",)

    # pylint: disable=too-many-branches
    def __init__(
        self, iterable: Optional[Iterable[atomic.IntervalValue[atomic.TO]]] = None
    ) -> None:
        """
        Initialize an :class:`IntervalSet` instance.

        Arguments
        ---------
            iterable: :class:`Iterable <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple.
        """
        if iterable is None:
            iterable = []
        intervals = []
        for item in iterable:
            if item:
                intervals.append(atomic.Atomic.from_value(item))

        # pylint: disable=protected-access
        intervals = sorted(intervals, key=lambda elem: elem._lower)

        if intervals:
            current = copy.copy(intervals[0])
            for interval in intervals[1:]:
                if (
                    interval._lower <= current._upper
                    or interval._lower.value == current._upper.value
                    and (interval._lower.type == 0 or current._upper.type == 0)
                ):
                    current._upper = max(current._upper, interval._upper)
                else:
                    self._append(current)
                    current = copy.copy(interval)
            self._append(current)

    def __str__(self) -> str:
        """Return str(self)."""
        return " | ".join(str(interval) for interval in self)

    def __eq__(self, other):
        """Return self==other."""
        if not isinstance(other, IntervalSet):
            return NotImplemented
        # pylint: disable=protected-access
        return self._intervals == other._intervals

    def __le__(self, other):
        """
        Test whether every element in the set is in *other*.

        Arguments
        ---------
            other: :class:`Iterable <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple.

        Returns
        -------
            :data:`True <python:True>`
                If the set is subset of the *other*.

        See also
        --------

            issubset: subset test.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;2] | [6;7) | (8;9) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> a <= b
            True
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self._issubset(other)

    def __lt__(self, other):
        """
        Return self<other.

        Test whether the set is a proper subset of *other*, that is, self <= *other* and
        self != *other*.

        Arguments
        ---------
            other: :class:`Iterable <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple.

        Returns
        -------
            :data:`True <python:True>`
                If the set is a proper subset of the *other*.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;2] | [6;7) | (8;9) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> a < b
            True
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self._issubset(other, strict=True)

    def __ge__(self, other):
        """
        Test whether every element in *other* is in the set.

        Arguments
        ---------
            other: :class:`Iterable <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple.

        Returns
        -------
            :data:`True <python:True>`
                If the set is superset of the *other*.

        See also
        --------

            issuperset: superset test.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;2] | [6;7) | (8;9) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> a >= b
            False
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return other._issubset(self)

    def __gt__(self, other):
        """
        Return self>other.

        Test whether the set is a proper superset of *other*, that is,
        self >= *other* and self != *other*.

        Arguments
        ---------
            other: :class:`Iterable <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple.

        Returns
        -------
            :data:`True <python:True>`
                If the set is a proper superset of the *other*.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;2] | [6;7) | (8;9) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> a > b
            False
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return other._issubset(self, strict=True)

    def __len__(self) -> int:
        """
        Return the number of inner intervals.

        Returns
        -------
            int
                The number of inner intervals.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> len(a)
            4
        """
        return len(self._intervals)  # type: ignore

    def __getitem__(self, item):
        """
        Return the nth interval. The array access operator supports slicing.

        Arguments
        ---------
            item: int
                The interval requested.

        Returns
        -------
            The nth interval

        Raises
        ------
            IndexError
                If the *item* is out of range.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> print(a[0])
            [2;2]
            >>> print(a[2])
            (8;9)
            >>> print(a[2])
            (8;9)
            >>> print(a[1:3])
            [6;7) | (8;9)
        """
        if isinstance(item, slice):
            return self.__class__(self._intervals[item])
        return self._intervals[item]

    def __iter__(self) -> Iterator[atomic.Interval[atomic.TO]]:
        """
        Return an iterator over the intervals.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 9, None), (10, 11, True, True)]
            ... )
            >>> print(list(str(interval) for interval in a))
            ['[2;2]', '[6;7)', '(8;9)', '[10;11]']
        """
        return iter(self._intervals)  # type: ignore

    def __and__(self, other) -> "IntervalSet":
        """
        Return the intersection of self with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`IntervalSet`
                The intersection of self with *other*.

        See also
        --------

            intersection: Intersection with several interval sets.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int]([(2, 8), (10, 11, True, True)])
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;8) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> print(a & b)
            [2;7) | [10;11]
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.intersection(other)

    def __or__(self, other) -> "IntervalSet":
        """
        Return the union of self with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`IntervalSet`
                The union of self with *other*.

        See also
        --------

            union: Union with several interval sets.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int]([(2, 8), (10, 11, True, True)])
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;8) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> print(a | b)
            [0;13)
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.union(other)

    def __sub__(self, other) -> "IntervalSet":
        """
        Return the difference of self with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`IntervalSet`
                The difference of self with *other*.

        See also
        --------

            difference: Difference with several interval sets.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int]([(2, 8), (10, 11, True, True)])
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;8) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> print(a - b)
            [7;8)
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.difference(other)

    def __xor__(self, other) -> "IntervalSet":
        """
        Return the symmetric difference of self with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`IntervalSet`
                The symmetric difference of self with *other*.

        See also
        --------

            symmetric_difference: Symmetric difference with several interval sets.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int]([(2, 8), (10, 11, True, True)])
            >>> b = FrozenIntervalSet[int]([(0, 7), (8, 13)])
            >>> print(a)
            [2;8) | [10;11]
            >>> print(b)
            [0;7) | [8;13)
            >>> print(a ^ b)
            [0;2) | [7;10) | (11;13)
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        return self.symmetric_difference(other)

    def __invert__(self) -> "IntervalSet":
        """
        Return the complement of self.

        Returns
        -------
            :class:`IntervalSet`
                The complement of self.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int]([(2, 8), (10, 11, True, True)])
            >>> print(a)
            [2;8) | [10;11]
            >>> print(~a)
            (-inf;2) | [8;10) | (11;+inf)
        """
        result = self.__class__()
        for interval in self._invert():
            if interval:
                result._append(interval)
        return result

    def __reversed__(self) -> Iterator[atomic.Interval[atomic.TO]]:
        """
        Implement the reversed iterator.

        Returns
        -------
            :class:`Iterator[Interval]  <python:typing.Iterator>`
                An iterator over the reversed interval collection
        """
        return reversed(self._intervals)  # type: ignore

    def _invert(self) -> Iterator[atomic.Interval[atomic.TO]]:
        value: Union[atomic.TO, values.NegativeInfinity] = -values.INFINITY
        closed = False
        for interval in self:
            yield atomic.Atomic[atomic.TO].from_tuple(
                (value, interval.lower_value, closed, not interval.lower_closed)
            )
            value = interval.upper_value
            closed = not interval.upper_closed
        yield atomic.Interval.lower_limit(value=value, closed=closed)

    @abstractmethod
    def _append(self, item) -> None:
        raise NotImplementedError

    @abstractmethod
    def _bisect_left(self, search, lo=0, hi=None):  #  pylint: disable=invalid-name
        raise NotImplementedError

    @staticmethod
    def _items(*args):
        items = []
        for intervals in args:
            if intervals is None:
                raise TypeError("None object is not iterable")
            if not isinstance(intervals, IntervalSet):
                intervals = FrozenIntervalSet[atomic.TO](intervals)
            items.append(intervals)
        return items

    def _intersection(self, *args) -> Iterator[atomic.Interval[atomic.TO]]:
        # pylint: disable=protected-access,no-member
        items = IntervalSet._items(*args)

        if not self:
            return

        # prepare a heap of (sup, index, intervals, cursor)
        heap = []
        interval = self[0]

        # update max_inf if necessary
        max_inf = interval._lower

        # insert the first interval of self
        heap.append((interval._upper, 0, self, 0))

        for index, intervals in enumerate(items):
            if not intervals:
                return
            interval = intervals[0]
            # update max_inf if necessary
            max_inf = max(max_inf, interval._lower)
            heap.append((interval._upper, index + 1, intervals, 0))

        # transform into a priority queue O(n)
        heapq.heapify(heap)

        # Loop for each interval (there is k-n intervals remaining)
        while True:
            # get the minimal sup
            (sup, index, intervals, cursor) = heap[0]

            # output interval as a tuple if not empty
            if max_inf <= sup:
                interval = atomic.Interval[atomic.TO]()
                interval._lower = max_inf
                interval._upper = sup
                yield interval

            search = atomic.Atomic.from_value(max_inf.value)

            # get the next interval for this list using array bisection algorithm
            cursor = intervals._bisect_left(search, lo=cursor + 1)
            if cursor < len(intervals):
                # update max_inf if necessary
                max_inf = max(max_inf, intervals[cursor]._lower)

                # remove first item and insert new item in O(log(n))
                heapq.heapreplace(
                    heap, (intervals[cursor]._upper, index, intervals, cursor)
                )
            else:
                return

    def _union(self, *args) -> Iterator[atomic.Interval[atomic.TO]]:
        # pylint: disable=protected-access,no-member
        items = IntervalSet._items(*args)

        # prepare a heap of (inf, index, intervals, cursor)
        heap = []
        if self:
            # insert the first interval of self
            heap.append((self[0]._lower, 0, self, 0))

        for index, intervals in enumerate(items):
            if intervals:
                heap.append((intervals[0]._lower, index + 1, intervals, 0))

        max_sup = atomic.Mark(value=-values.INFINITY, type=1)
        min_inf = atomic.Mark(value=+values.INFINITY, type=-1)

        # transform into a priority queue O(n)
        heapq.heapify(heap)

        # Loop for each interval (there is k-n intervals remaining)
        while heap:
            # get the minimal inf
            (inf, index, intervals, cursor) = heap[0]
            sup = intervals[cursor]._upper

            # output interval as a tuple if not empty
            if inf > max_sup and not inf.near(max_sup):
                if min_inf <= max_sup:
                    interval = atomic.Interval[atomic.TO]()
                    interval._lower = min_inf
                    interval._upper = max_sup
                    yield interval
                min_inf = inf
            max_sup = max(max_sup, sup)

            search = atomic.Atomic.from_value(max_sup.value)

            # get the next interval for this list using array bisection algorithm
            cursor = intervals._bisect_left(search, lo=cursor + 1)
            if cursor < len(intervals):
                # remove first item and insert new item in O(log(n))
                heapq.heapreplace(
                    heap, (intervals[cursor]._lower, index, intervals, cursor)
                )
            else:
                heapq.heappop(heap)

        if min_inf <= max_sup:
            interval = atomic.Interval[atomic.TO]()
            interval._lower = min_inf
            interval._upper = max_sup
            yield interval

    def isdisjoint(self, other: Iterable[atomic.IntervalValue[atomic.TO]]) -> bool:
        """
        Return the disjointness between self and *other*.

        Return :data:`True <python:True>` if the set has no elements in common with
        *other*. Sets are disjoint if and only if their intersection is the empty set.

        Arguments
        ---------
            other: :class:`IntervalSet`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :data:`True <python:True>`
                if the sets are disjoint,
            :data:`False <python:False>`
                otherwise.
        """
        try:
            next(self._intersection(other))
            return False
        except StopIteration:
            return True

    def issubset(self, other: Iterable[atomic.IntervalValue[atomic.TO]]) -> bool:
        """
        Return :data:`True <python:True>` if the set is a subset of the *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :data:`True <python:True>`
                if the set is a subset of the *other*,
            :data:`False <python:False>`
                otherwise.

        See also
        --------

            __le__: subset test.
        """
        return self._issubset(other)

    def issuperset(self, other: Iterable[atomic.IntervalValue[atomic.TO]]) -> bool:
        """
        Return :data:`True <python:True>` if the set is a superset of the *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :data:`True <python:True>`
                if the set is a superset of the *other*,
            :data:`False <python:False>`
                otherwise.

        See also
        --------

            __ge__: superset test.
        """
        other = FrozenIntervalSet[atomic.TO](other)
        # pylint: disable=protected-access
        return other._issubset(self)

    def _issubset(self, other: Iterable[atomic.IntervalValue[atomic.TO]], strict=False):
        iterator = iter(self)
        if not isinstance(other, IntervalSet):
            other = FrozenIntervalSet[atomic.TO](other)
        cursor = 0
        subset = False
        try:
            while True:
                # pylint: disable=protected-access
                interval: atomic.Interval[atomic.TO] = next(iterator)
                cursor = other._bisect_left(interval, lo=cursor)
                during = other[cursor]
                if interval._lower < during._lower or interval._upper > during._upper:
                    return False
                if interval._lower > during._lower or interval._upper < during._upper:
                    subset = True
        except StopIteration:
            return not strict or subset

    def intersection(
        self, *args: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> "IntervalSet[atomic.TO]":
        """
        Return the intersection of a list of sorted interval sets.

        Arguments
        ---------
            *args : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :class:`IntervalSet`
                a sorted interval set

        Raises
        ------
            TypeError
                if an argument is not iterable.

        See also
        --------

            __and__: An intersection is equivalent to several :meth: `__and__`.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> print(
            ...     FrozenIntervalSet[int]([(1, 3), (4, 10)]).intersection(
            ...         FrozenIntervalSet[int]([(2, 5), (6, 8)]),
            ...         FrozenIntervalSet[int]([(2, 3), (4, 11)])
            ...     )
            ... )
            [2;3) | [4;5) | [6;8)
            >>> print(FrozenIntervalSet[int]().intersection())
            <BLANKLINE>
            >>> print(FrozenIntervalSet[int]([(1, 3), (4, 10)]).intersection())
            [1;3) | [4;10)
            >>> print(FrozenIntervalSet[int]([(1, 3)]).intersection(
            ...     FrozenIntervalSet[int]([(4, 10)]))
            ... )
            <BLANKLINE>
            >>> print(FrozenIntervalSet[int]([(1, 3, True, True)]).intersection(
            ...     FrozenIntervalSet[int]([(3, 10)]))
            ... )
            [3;3]
            >>> print(FrozenIntervalSet[int]([(1, 3)]).intersection(
            ...     FrozenIntervalSet[int]([(1, 3)]))
            ... )
            [1;3)
            >>> print(
            ...     FrozenIntervalSet[int](
            ...         [(0, 2), (5, 10), (13, 23), (24, 25)]
            ...     ).intersection(
            ...         FrozenIntervalSet[int](
            ...             [
            ...                 (1, 5, True, True),
            ...                 (8, 12),
            ...                 (15, 18),
            ...                 (20, 24, True, True)
            ...             ]
            ...         ),
            ...         FrozenIntervalSet[int](
            ...             [(1, 9), (16, 30)]
            ...         )
            ...     )
            ... )
            [1;2) | [5;5] | [8;9) | [16;18) | [20;23) | [24;24]
        """
        result = self.__class__()
        for item in self._intersection(*args):
            # pylint: disable=protected-access
            result._append(item)
        return result

    def union(
        self, *args: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> "IntervalSet[atomic.TO]":
        """
        Return the union of a list of sorted interval sets.

        Arguments
        ---------
            *args : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :class:`IntervalSet`
                a sorted interval set

        Raises
        ------
            TypeError
                if an argument is not iterable.

        See also
        --------

            __or__: An union is equivalent to several :meth: `__or__`.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> print(
            ...     FrozenIntervalSet[int]([(1, 3), (4, 10)]).union(
            ...         FrozenIntervalSet[int]([(2, 5), (6, 8)]),
            ...         FrozenIntervalSet[int]([(2, 3), (4, 11)])
            ...     )
            ... )
            [1;11)
            >>> print(FrozenIntervalSet[int]().union())
            <BLANKLINE>
            >>> print(FrozenIntervalSet[int]([(1, 3), (4, 10)]).union())
            [1;3) | [4;10)
            >>> print(FrozenIntervalSet[int]([(1, 3)]).union(
            ...     FrozenIntervalSet[int]([(4, 10)]))
            ... )
            [1;3) | [4;10)
            >>> print(FrozenIntervalSet[int]([(1, 3, True, True)]).union(
            ...     FrozenIntervalSet[int]([(3, 10)]))
            ... )
            [1;10)
            >>> print(FrozenIntervalSet[int]([(1, 3)]).union(
            ...     FrozenIntervalSet[int]([(1, 3)]))
            ... )
            [1;3)
            >>> print(
            ...     FrozenIntervalSet[int]([(0, 2), (5, 10), (13, 23), (24, 25)]).union(
            ...         FrozenIntervalSet[int](
            ...             [
            ...                 (1, 5, True, True),
            ...                 (8, 12),
            ...                 (15, 18),
            ...                 (20, 24, True, True)
            ...             ]
            ...         ),
            ...         FrozenIntervalSet[int](
            ...             [(1, 9), (16, 30)]
            ...         )
            ...     )
            ... )
            [0;12) | [13;30)
        """
        # TODO Precise algorithmic complexity for union and intersection.
        result = self.__class__()
        for item in self._union(*args):
            # pylint: disable=protected-access
            result._append(item)
        return result

    def difference(
        self, *args: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> "IntervalSet[atomic.TO]":
        """
        Return the difference with of a list of sorted interval sets.

        Arguments
        ---------
            *args : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :class:`IntervalSet`
                a sorted interval set

        Raises
        ------
            TypeError
                if an argument is not iterable.

        See also
        --------

            __sub__: A difference is equivalent to several :meth: `__sub__`.
        """
        return self.intersection(~self.__class__().union(*args))

    def symmetric_difference(
        self, other: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> "IntervalSet[atomic.TO]":
        """
        Return the symmetric difference with of another sorted interval set.

        Arguments
        ---------
            other : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Returns
        -------
            :class:`IntervalSet`
                a sorted interval set.

        Raises
        ------
            TypeError
                if *other* is not iterable.

        See also
        --------

            __xor__: A symmetric difference is equivalent to several :meth: `__xor__`.
        """
        if not isinstance(other, IntervalSet):
            other = FrozenIntervalSet[atomic.TO](other)
        return (self | other) - (self & other)

    def copy(self) -> "IntervalSet":
        """
        Create a shallow copy of self.

        Returns
        -------
            :class:`IntervalSet`
                A shallow copy of self.
        """
        result = self.__class__()
        # pylint: disable=protected-access,attribute-defined-outside-init
        result._intervals = self._intervals.copy()  # type: ignore
        return result

    def select(
        self, value: atomic.IntervalValue[atomic.TO], strict: bool = True
    ) -> Iterator[atomic.Interval[atomic.TO]]:
        """
        Select all intervals that have a non-empty intersection with *value*.

        Arguments
        ---------
            value: \
                    :class:`Atomic`, \
                    :class:`TO <TotallyOrdered>`\
                    :class:`Tuple[TO, TO] <python:tuple>`, \
                    :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`, \
                    :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] \
                        <python:tuple>`
                The value to search
            strict: bool
                Is the comparison strict?

        Returns
        -------
            :class:`Iterator[Interval] <python:typing.Iterator>`
                An iterator over the selected intervals.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet[int](
            ...     [2, (6, 7), (8, 10, None), (11, 13, True, True)]
            ... )
            >>> print(list(str(interval) for interval in a.select((5, 9))))
            ['[6;7)']
            >>> print(list(str(interval) for interval in a.select((2, 9))))
            ['[2;2]', '[6;7)']
            >>> print(
            ...     list(str(interval) for interval in a.select((2, 9), strict=False))
            ... )
            ['[2;2]', '[6;7)', '(8;10)']
        """
        if not value:
            return
        interval = atomic.Atomic.from_value(value)
        index = self._bisect_left(interval)
        if strict and index < len(self) and self[index].lower < interval.lower:
            index += 1
        while index < len(self):
            other = self[index]
            if other.lower <= interval.upper:
                if other.upper > interval.upper:
                    if strict:
                        return
                    yield other
                    return
                yield other
            else:
                return
            index += 1


class FrozenIntervalSet(
    Generic[atomic.TO],
    # pylint: disable=unsubscriptable-object
    IntervalSet[atomic.TO],
):
    """
    Frozen Interval Set class.

    The :class:`FrozenIntervalSet` class (which inherits from the :class:`IntervalSet`
    class) is designed to hold frozen disjoint intervals.
    """

    __slots__ = ("_hash",)

    # pylint: disable=too-many-branches
    def __init__(
        self, iterable: Optional[Iterable[atomic.IntervalValue[atomic.TO]]] = None
    ) -> None:
        """
        Initialize a :class:`FrozenIntervalSet` instance.

        Arguments
        ---------
            iterable: :class:`Iterable <python:typing.Iterable>`
                An optional iterable of:

                * :class:`Atomic`
                * :class:`TO <TotallyOrdered>`
                * :class:`Tuple[TO, TO] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] \
                        <python:tuple>`

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet([2, (6, 7), (8, 9, None), (10, 11, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;9) | [10;11]
        """
        self._intervals: List[atomic.Interval[atomic.TO]] = []
        self._hash: Optional[int] = None
        super().__init__(iterable)

    def __hash__(self) -> int:
        """
        A :class:`FrozenIntervalSet` instance is hashable.

        It can be used as key in dictionaries.
        """
        if self._hash is None:
            self._hash = hash(tuple(self._intervals))
        return self._hash

    def __contains__(self, value) -> bool:
        """
        Test the membership.

        Arguments
        ---------
            value: object
                The value to search.

        Returns
        -------
            :data:`True <python:True>`
                if the *value* is contained in self.
            :data:`False <python:False>`
                 otherwise.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet([(2, 8), (10, 11, True, True)])
            >>> print(a)
            [2;8) | [10;11]
            >>> (10,13) in a
            False
        """
        try:
            interval = atomic.Atomic.from_value(value)
            index = self._bisect_left(interval)
            return (
                index < len(self)
                and self[index].lower <= interval.lower
                and interval.upper <= self[index].upper
            )
        except TypeError:
            return False

    def __getitem__(self, item):
        """
        Return the nth interval. The array access operator supports slicing.

        Arguments
        ---------
            item: Union[int, slice]
                The interval requested.

        Returns
        -------
            The nth interval

        Raises
        ------
            IndexError
                If the *item* is out of range.

        Examples
        --------

            >>> from part import FrozenIntervalSet
            >>> a = FrozenIntervalSet([2, (6, 7), (8, 9, None), (10, 11, True, True)])
            >>> print(a[0])
            [2;2]
            >>> print(a[2])
            (8;9)
            >>> print(a[2])
            (8;9)
            >>> print(a[1:3])
            [6;7) | (8;9)
        """
        if isinstance(item, slice):
            result = self.__class__()
            result._intervals = self._intervals[item]
            return result
        return super().__getitem__(item)

    # pylint: disable=invalid-name
    def _bisect_left(self, search, lo=0, hi=None):
        if hi is None:
            hi = len(self)
        return bisect.bisect_left(self._intervals, search, lo=lo, hi=hi)

    def _append(self, item) -> None:
        self._intervals.append(item)


# pylint: disable=too-many-ancestors
class MutableIntervalSet(
    Generic[atomic.TO],
    # pylint: disable=unsubscriptable-object
    IntervalSet[atomic.TO],
    MutableSet[atomic.Interval[atomic.TO]],
):
    """
    Mutable Interval Set class.

    The :class:`MutableIntervalSet` class (which inherits from the :class:`IntervalSet`
    class) is designed to hold mutable disjoint sorted intervals.
    """

    __slots__ = ()

    # pylint: disable=too-many-branches
    def __init__(
        self, iterable: Optional[Iterable[atomic.IntervalValue[atomic.TO]]] = None
    ) -> None:
        """
        Initialize a :class:`MutableIntervalSet` instance.

        Arguments
        ---------
            iterable: :class:`Iterable <python:typing.Iterable>`
                An optional iterable of either

                * :class:`Atomic`
                * :class:`TO <TotallyOrdered>`
                * :class:`Tuple[TO, TO] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] <python:tuple>`

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
        """
        self._intervals: SortedSet = SortedSet()
        super().__init__(iterable)

    def __contains__(self, item) -> bool:
        """
        Test the membership.

        Arguments
        ---------
            item: object
                The value to search.

        Returns
        -------
            :data:`True <python:True>`
                if the *value* is contained in self.
            :data:`False <python:False>`
                 otherwise.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([(2, 8), (10, 11, True, True)])
            >>> print(a)
            [2;8) | [10;11]
            >>> (10,13) in a
            False
        """
        return item in self._intervals

    def __ior__(self, other) -> "MutableIntervalSet[atomic.TO]":  # type: ignore
        """
        Update self with the union *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`MutableIntervalSet`
                The updated :class:`MutableIntervalSet`.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> b = MutableIntervalSet([(0, 7), (8, 12)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> print(b)
            [0;7) | [8;12)
            >>> a |= b
            >>> print(a)
            [0;7) | [8;13]
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        self.update(other)
        return self

    def __iand__(self, other) -> "MutableIntervalSet[atomic.TO]":
        """
        Update self with the intersection with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`MutableIntervalSet`
                The updated :class:`MutableIntervalSet`.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> b = MutableIntervalSet([(0, 7), (8, 12)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> print(b)
            [0;7) | [8;12)
            >>> a &= b
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;12)
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        self.intersection_update(other)
        return self

    def __isub__(self, other) -> "MutableIntervalSet[atomic.TO]":
        """
        Update self with the difference with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.

        Returns
        -------
            :class:`MutableIntervalSet`
                The updated :class:`MutableIntervalSet`.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> b = MutableIntervalSet([(0, 7), (8, 12)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> print(b)
            [0;7) | [8;12)
            >>> a -= b
            >>> print(a)
            [12;13]
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        self.difference_update(other)
        return self

    def __ixor__(self, other) -> "MutableIntervalSet[atomic.TO]":  # type: ignore
        """
        Update self with the symmetric difference with *other*.

        Arguments
        ---------
            other: :class:`IntervalSet`
                Another interval set.
        Returns
        -------
            :class:`MutableIntervalSet`
                The updated :class:`MutableIntervalSet`.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> b = MutableIntervalSet([(0, 7), (8, 12)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> print(b)
            [0;7) | [8;12)
            >>> a ^= b
            >>> print(a)
            [0;2) | (2;6) | [8;8] | [10;11) | [12;13]
        """
        if not isinstance(other, IntervalSet):
            return NotImplemented
        self.symmetric_difference_update(other)
        return self

    # pylint: disable=invalid-name
    def _bisect_left(self, search, lo=0, hi=None) -> int:
        if hi is None:
            hi = len(self)
        cursor = self._intervals.bisect_left(search)
        if cursor < lo:
            cursor = lo
        if cursor >= hi:
            cursor = hi
        return cursor

    def _append(self, item) -> None:
        self._intervals.add(item)

    def update(self, *args: Iterable[atomic.IntervalValue[atomic.TO]]) -> None:
        """
        Update the set, keeping only elements found in it and all others.

        Arguments
        ---------
            *args : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Raises
        ------
            TypeError
                if an argument is not iterable.
        """
        result = self.union(*args)
        # pylint: disable=protected-access
        self._intervals = result._intervals  # type: ignore

    def intersection_update(
        self, *args: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> None:
        """
        Update the set, keeping only elements found in it and all others.

        Arguments
        ---------
            *args : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Raises
        ------
            TypeError
                if an argument is not iterable.
        """
        result = self.intersection(*args)
        # pylint: disable=protected-access
        self._intervals = result._intervals  # type: ignore

    def difference_update(
        self, *args: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> None:
        """
        Update the set, removing elements found in others.

        Arguments
        ---------
            *args : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Raises
        ------
            TypeError
                if an argument is not iterable.
        """
        result = self.difference(*args)
        # pylint: disable=protected-access
        self._intervals = result._intervals  # type: ignore

    def symmetric_difference_update(
        self, other: Iterable[atomic.IntervalValue[atomic.TO]]
    ) -> None:
        """
        Update the set, keeping only elements found in either set, but not in both.

        Arguments
        ---------
            other : :class:`Iterable[IntervalValue] <python:typing.Iterable>`
                An iterable of :class:`Atomic` or valid tuple for an interval
                creation.

        Raises
        ------
            TypeError
                if *other* is not iterable.
        """
        result = self.symmetric_difference(other)
        # pylint: disable=protected-access
        self._intervals = result._intervals  # type: ignore

    def add(self, value: atomic.IntervalValue[atomic.TO]) -> None:
        """
        Add element *value* to the set.

        Arguments
        ---------
            value: :class:`IntervalValue`
                The value to add:

                * :class:`Atomic`
                * :class:`TO <TotallyOrdered>`
                * :class:`Tuple[TO, TO] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] <python:tuple>`

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> a.add((2, 6))
            >>> print(a)
            [2;7) | (8;10) | [11;13]
        """
        if not value:
            return

        interval = atomic.Atomic.from_value(value)
        self._intervals = SortedSet(self._union(FrozenIntervalSet([interval])))

    def remove(self, value: atomic.IntervalValue[atomic.TO]) -> None:
        """
        Remove element *value* from the set.

        Arguments
        ---------
            value: :class:`IntervalValue`
                The value to remove:

                * :class:`Atomic`
                * :class:`TO <TotallyOrdered>`
                * :class:`Tuple[TO, TO] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] <python:tuple>`

        Raises
        ------
            KeyError
                if *value* is not contained in the set.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> try:
            ...     a.remove((2, 8))
            ... except KeyError as e:
            ...     print(e)
            '(2, 8)'
        """
        if not value:
            return

        interval = atomic.Atomic.from_value(value)
        index = self._bisect_left(interval)
        if index < len(self) and interval.during(self[index], strict=False):
            self._intervals = SortedSet(self._intersection(~interval))
        else:
            raise KeyError(f"{value}")

    def discard(self, value: atomic.IntervalValue[atomic.TO]) -> None:
        """
        Discard element *value* from the set.

        Arguments
        ---------
            value: :class:`IntervalValue`
                The value to discard:

                * :class:`Atomic`
                * :class:`TO <TotallyOrdered>`
                * :class:`Tuple[TO, TO] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] <python:tuple>`

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> a.discard((2, 8))
            >>> print(a)
            (8;10) | [11;13]
        """
        if not value:
            return

        interval = atomic.Atomic.from_value(value)
        self._intervals = SortedSet(self._intersection(~interval))

    def pop(self) -> atomic.Interval[atomic.TO]:
        """
        Get the first interval.

        Returns
        -------
            :class:`part.Interval`
                The first interval.

        Raises
        ------
            KeyError
                if the set is empty.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> print(a.pop())
            [2;2]
            >>> print(a)
            [6;7) | (8;10) | [11;13]
        """
        try:
            return self._intervals.pop(0)
        except IndexError:
            raise KeyError("pop from an empty set")

    def clear(self) -> None:
        """
        Remove all elements from the set.

        Examples
        --------

            >>> from part import MutableIntervalSet
            >>> a = MutableIntervalSet([2, (6, 7), (8, 10, None), (11, 13, True, True)])
            >>> print(a)
            [2;2] | [6;7) | (8;10) | [11;13]
            >>> a.clear()
            >>> print(a)
            <BLANKLINE>
        """
        self._intervals = SortedSet()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
