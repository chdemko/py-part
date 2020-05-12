"""Interval dictionaries module."""

import bisect
import collections
from abc import ABCMeta, abstractmethod
from typing import Union, Mapping, Iterable, Tuple, Any, List, Optional, Iterator

# pylint: disable=import-error
from sortedcontainers import SortedSet  # type: ignore

from part import atomic


class IntervalDict(collections.abc.Mapping, metaclass=ABCMeta):
    """
    The :class:`IntervalDict` abstract class can hold dict of disjoint sorted intervals.

    It implements the :class:`Mapping <python:typing.Mapping>` protocol. It is
    implemented in two concrete classes:

    * :class:`FrozenIntervalDict`
    * :class:`MutableIntervalDict`
    """

    __slots__ = ("_intervals", "_mapping")

    def __init__(self) -> None:
        """Initialize :class:`IntervalDict` instances."""
        self._intervals = None
        self._mapping: dict = {}

    def __str__(self) -> str:
        """
        Return str(self).

        Returns
        -------
            str
                The string representation of self.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
        """
        return str(
            {
                str(interval): self._mapping[interval]
                for interval in self._intervals  # type: ignore
            }
        )

    def __len__(self) -> int:
        """
        Return the number of inner intervals.

        Returns
        -------
            int
                The number of inner intervals.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> len(a)
            3
        """
        return len(self._intervals)  # type: ignore

    def __iter__(self) -> Iterator[atomic.Interval]:
        """
        Return an iterator over the intervals.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(list(str(interval) for interval in a))
            ['[10;15)', '[20;25)', '[30;35)']
        """
        return iter(self._intervals)  # type: ignore

    def __contains__(self, value) -> bool:
        """
        Test the membership.

        Arguments
        ---------
            value: \
                    :class:`Atomic`, \
                    :class:`Tuple[Any, Any] <python:tuple>`, \
                    :class:`Tuple[Any, Any, Optional[bool]] <python:tuple>`, \
                    :class:`Tuple[Any, Any, Optional[bool], Optional[bool]] \
                        <python:tuple>`
                The value to search.

        Returns
        -------
            :data:`True <python:True>`
                if the *value* is contained in self.
            :data:`False <python:False>`
                 otherwise.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> (10,13) in a
            True
            >>> (13,17) in a
            False
        """
        if value is atomic.EMPTY:
            return True
        interval = atomic.Atomic.from_value(value)
        index = self._bisect_left(interval)
        if index < len(self._intervals):  # type: ignore
            other = self._intervals[index]  # type: ignore
            return interval.during(other, strict=False)
        return False

    def __getitem__(self, key: Union[slice, atomic.IntervalValue]) -> Any:
        """
        Return a value using either a slice or an interval value.

        Arguments
        ---------
            key: Union[IntervalValue, slice]
                The interval requested.

        Returns
        -------
            The found value

        Raises
        ------
            KeyError
                If the *key* is out of range.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> print(a[12])
            1
            >>> print(a[(21, 24)])
            2
            >>> try:
            ...     print(a[(24, 26)])
            ... except KeyError as e:
            ...     print(e)
            '(24, 26)'
            >>> print(a[24:26])
            {'[24;25)': 2}
        """
        if isinstance(key, slice):
            search = IntervalDict._from_slice(key)
            result = []
            for found in self.select(search, strict=False):
                value = self._mapping[found]
                interval = atomic.Interval()
                interval._lower = max(found.lower, search.lower)
                interval._upper = min(found.upper, search.upper)
                result.append((interval, value))
            # pylint: disable=too-many-function-args
            return self.__class__(result)  # type: ignore
        interval = IntervalDict._interval(key)
        index = self._bisect_left(interval)
        if index < len(self._intervals):  # type: ignore
            other = self._intervals[index]  # type: ignore
            if interval.during(other, strict=False):
                return self._mapping[self._intervals[index]]  # type: ignore
        raise KeyError(str(key))

    def copy(self) -> "IntervalDict":
        """
        Return a shallow copy of the dictionary.

        Returns
        -------
            :class:`IntervalDict`
                A shallow copy of the dictionary.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> b = a.copy()
            >>> print(b)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> a == b
            True
            >>> a is b
            False
        """
        copy = self.__class__()
        # pylint: disable=protected-access
        copy._intervals = self._intervals.copy()  # type: ignore
        copy._mapping = self._mapping.copy()
        return copy

    @staticmethod
    def _interval(key):
        if isinstance(key, slice):
            return IntervalDict._from_slice(key)
        return atomic.Atomic.from_value(key)

    @staticmethod
    def _from_slice(key):
        if key.step is not None:
            raise ValueError("step is not authorized in slices")
        return atomic.Interval(key.start, key.stop)

    def select(
        self, value: atomic.IntervalValue, strict: bool = True
    ) -> Iterator[atomic.Interval]:
        """
        Select all intervals that have a non-empty intersection with *value*.

        Arguments
        ---------
            value: \
                    :class:`Atomic`, \
                    :class:`Tuple[Any, Any] <python:tuple>`, \
                    :class:`Tuple[Any, Any, Optional[bool]] <python:tuple>`, \
                    :class:`Tuple[Any, Any, Optional[bool], Optional[bool]] \
                        <python:tuple>`
                The value to search
            strict: bool
                Is the comparison strict?

        Returns
        -------
            :class:`Iterator[Tuple[Interval, Any]] <python:typing.Iterator>`
                An iterator over the selected items.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict(
            ...     [
            ...         (2, 1),
            ...         ((6, 7), 2),
            ...         ((8, 10, None), 3),
            ...         ((11, 13, True, True), 4)
            ...     ]
            ... )
            >>> [str(interval) for interval in a.select((5, 9))]
            ['[6;7)']
            >>> [str(interval) for interval in a.select((2, 9))]
            ['[2;2]', '[6;7)']
            >>> [str(interval) for interval in a.select((2, 9), strict=False)]
            ['[2;2]', '[6;7)', '(8;10)']
        """
        if value is atomic.EMPTY:
            return
        interval = atomic.Atomic.from_value(value)
        index = self._bisect_left(interval)
        if (
            strict
            and index < len(self)
            and self._intervals[index].lower < interval.lower  # type: ignore
        ):
            index += 1
        while index < len(self):
            other = self._intervals[index]  # type: ignore
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

    def compress(self) -> "IntervalDict":
        """
        Compress a dictionary.

        Returns
        -------
            :class:`IntervalDict`
                A new dictionary where all useless intervals have been removed.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict(
            ...     {
            ...         (10, 15): 1,
            ...         (14, 25): 1,
            ...         (30, 35): 2,
            ...         (33, 45): 2
            ...     }
            ... )
            >>> print(a)
            {'[10;14)': 1, '[14;25)': 1, '[30;33)': 2, '[33;45)': 2}
            >>> b = a.compress()
            >>> print(b)
            {'[10;25)': 1, '[30;45)': 2}
        """
        result = self.__class__()
        intervals = []
        if self:
            iterator = iter(self)
            current = atomic.Atomic.from_value(next(iterator))
            value = self._mapping[current]
            while True:
                # pylint: disable=protected-access
                try:
                    interval = next(iterator)
                    if self._mapping[interval] == value and current.upper.near(
                        interval.lower
                    ):
                        current._upper = interval.upper
                    else:
                        intervals.append(current)
                        result._mapping[current] = value
                        current = atomic.Atomic.from_value(interval)
                        value = self._mapping[current]
                except StopIteration:
                    intervals.append(current)
                    result._update(intervals)
                    result._mapping[current] = value
                    break
        return result

    @abstractmethod
    def _bisect_left(self, search):  #  pylint: disable=invalid-name
        raise NotImplementedError

    @abstractmethod
    def _update(self, intervals) -> None:
        raise NotImplementedError


class FrozenIntervalDict(IntervalDict):
    """
    Frozen Interval Dictionary class.

    The :class:`FrozenIntervalDict` class (which inherits from the :class:`IntervalDict`
    class) is designed to hold frozen dict of disjoint intervals.
    """

    __slots__ = ("_hash",)

    def __init__(
        self,
        iterable: Optional[
            Union[
                Mapping[atomic.IntervalValue, Any],
                Iterable[Tuple[atomic.IntervalValue, Any]],
            ]
        ] = None,
    ) -> None:
        """
        Initialize a :class:`FrozenIntervalDict` instance.

        Arguments
        ---------
            iterable:
                :class:`Union[Mapping, Iterable[Tuple[atomic.IntervalValue, Any]]] \
                    <python:typing.Union>`, \
                optional
                An optional iterable.
        """
        super().__init__()
        self._hash: Optional[int] = None
        interval_dict = MutableIntervalDict(iterable)
        self._intervals: List[atomic.Interval] = list(  # type: ignore
            interval_dict._intervals
        )
        self._mapping = interval_dict._mapping

    def __hash__(self) -> int:
        """
        A :class:`FrozenIntervalDict` instance is hashable.

        It can be used as key in dictionaries.
        """
        if self._hash is None:
            self._hash = hash(frozenset(self._mapping.items()))
        return self._hash

    def _bisect_left(self, search) -> int:
        return bisect.bisect_left(self._intervals, search)

    def _update(self, intervals) -> None:
        self._intervals = intervals


# pylint: disable=too-many-ancestors
class MutableIntervalDict(IntervalDict, collections.abc.MutableMapping):
    """
    Mutable Interval Dictionary class.

    The :class:`MutableIntervalDict` class (which inherits from the
    :class:`IntervalDict` class) is designed to hold mutable dict of disjoint sorted
    intervals.
    """

    __slots__ = ("_default",)

    def __init__(
        self,
        iterable: Optional[
            Union[
                Mapping[atomic.IntervalValue, Any],
                Iterable[Tuple[atomic.IntervalValue, Any]],
            ]
        ] = None,
        default: Any = None,
    ) -> None:
        """
        Initialize a :class:`MutableIntervalDict` instance.

        Arguments
        ---------
            iterable:
                :class:`Union[Mapping, Iterable[Tuple[atomic.IntervalValue, Any]]] \
                    <python:typing.Union>`, \
                optional
                An optional iterable.

        Keyword arguments
        -----------------
            default: :class:`Callable[[], Any] <python:typing.Callable>`
                The default factory.

        Examples
        --------

            >>> from part import MutableIntervalDict, FrozenIntervalSet, Interval
            >>> a = MutableIntervalDict(default=set)
            >>> interval = Interval(1, 10)
            >>> value = 1
            >>> intervals = FrozenIntervalSet(a.select(interval, strict=False))
            >>> print(intervals)
            <BLANKLINE>
            >>> for other in ((interval & found)[0] for found in intervals):
            ...     a[other] = a[other].copy()
            ...     a[other].add(value)
            >>> for other in FrozenIntervalSet([interval]) - intervals:
            ...     a[other].add(value)
            >>> print(a)
            {'[1;10)': {1}}
            >>> interval = Interval(5, 20)
            >>> value = 2
            >>> intervals = FrozenIntervalSet(a.select(interval, strict=False))
            >>> print(intervals)
            [1;10)
            >>> for other in ((interval & found)[0] for found in intervals):
            ...     a[other] = a[other].copy()
            ...     a[other].add(value)
            >>> for other in FrozenIntervalSet([interval]) - intervals:
            ...     a[other].add(value)
            >>> print(a)
            {'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2}}
            >>> interval = Interval(10, 30)
            >>> value = 1
            >>> intervals = FrozenIntervalSet(a.select(interval, strict=False))
            >>> print(intervals)
            [10;20)
            >>> for other in ((interval & found)[0] for found in intervals):
            ...     a[other] = a[other].copy()
            ...     a[other].add(value)
            >>> for other in FrozenIntervalSet([interval]) - intervals:
            ...     a[other].add(value)
            >>> print(a)
            {'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {1, 2}, '[20;30)': {1}}
            >>> print(a.compress())
            {'[1;5)': {1}, '[5;20)': {1, 2}, '[20;30)': {1}}
        """
        super().__init__()
        self._default = default
        self._intervals: SortedSet = SortedSet()

        if isinstance(iterable, collections.abc.Mapping):
            for key, value in iterable.items():
                self[atomic.Atomic.from_value(key)] = value
        elif isinstance(iterable, collections.abc.Iterable):
            for key, value in iterable:  # type: ignore
                self[atomic.Atomic.from_value(key)] = value
        elif iterable is not None:
            raise TypeError(f"{type(iterable)} object is not iterable")

    def __getitem__(self, key: Union[slice, atomic.IntervalValue]) -> Any:
        """
        Return a value using either a slice or an interval value.

        Arguments
        ---------
            key: Union[IntervalValue, slice]
                The interval requested.

        Returns
        -------
            The found value

        Raises
        ------
            KeyError
                If the *key* is out of range.
        """
        try:
            return super().__getitem__(key)
        except KeyError:
            if self._default is not None:
                value = self._default()
                self[key] = value
                return value
            raise

    def __setitem__(self, key: Union[slice, atomic.IntervalValue], value) -> None:
        """
        Set a value using either a slice or an interval value.

        Arguments
        ---------
            key: Union[IntervalValue, slice]
                The interval requested.

        Raises
        ------
            KeyError
                If the *key* is out of range.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> a[12] = 4
            >>> print(a)
            {'[10;12)': 1, '[12;12]': 4, '(12;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> a[13:31] = 5
            >>> print(a)
            {'[10;12)': 1, '[12;12]': 4, '(12;13)': 1, '[13;31)': 5, '[31;35)': 3}
            >>> a[:] = 0
            >>> print(a)
            {'(-inf;+inf)': 0}
        """
        interval = IntervalDict._interval(key)
        if interval is not atomic.EMPTY:
            start = self._start(interval)
            stop = self._stop(interval)
            for index in range(start, stop):
                del self._mapping[self._intervals[index]]
            del self._intervals[start:stop]
            self._intervals.add(interval)
            self._mapping[interval] = value

    def __delitem__(self, key: Union[slice, atomic.IntervalValue]) -> None:
        """
        Delete a value using either a slice or an interval value.

        Arguments
        ---------
            key: Union[IntervalValue, slice]
                The interval requested.

        Raises
        ------
            KeyError
                If the *key* is out of range.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = MutableIntervalDict({(10, 15): 1, (20, 25): 2, (30, 35): 3})
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> del a[12]
            >>> print(a)
            {'[10;12)': 1, '(12;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> del a[13:31]
            >>> print(a)
            {'[10;12)': 1, '(12;13)': 1, '[31;35)': 3}
            >>> del a[:]
            >>> print(a)
            {}
        """
        interval = IntervalDict._interval(key)
        if interval is not atomic.EMPTY:
            start = self._start(interval)
            stop = self._stop(interval)
            for index in range(start, stop):
                del self._mapping[self._intervals[index]]
            del self._intervals[start:stop]

    def clear(self) -> None:
        """Remove all items from self (same as del self[:])."""
        self._intervals = SortedSet()
        self._mapping = {}

    def _start(self, interval):
        start = self._intervals.bisect_left(interval)
        if start < len(self._intervals):
            start_interval = self._intervals[start]
            start_value = self._mapping[start_interval]
            if self._intervals[start].overlaps(interval, strict=False):
                del self._intervals[start]
                del self._mapping[start_interval]
                if self._add(
                    (
                        start_interval.lower_value,
                        interval.lower_value,
                        start_interval.lower_closed,
                        not interval.lower_closed,
                    ),
                    start_value,
                ):
                    start += 1
            elif interval.overlaps(self._intervals[start], strict=False):
                del self._intervals[start]
                del self._mapping[start_interval]
                if self._add(
                    (
                        interval.upper_value,
                        start_interval.upper_value,
                        not interval.upper_closed,
                        start_interval.upper_closed,
                    ),
                    start_value,
                ):
                    start += 1
            elif interval.during(self._intervals[start], strict=False):
                del self._intervals[start]
                del self._mapping[start_interval]
                if self._add(
                    (
                        start_interval.lower_value,
                        interval.lower_value,
                        start_interval.lower_closed,
                        not interval.lower_closed,
                    ),
                    start_value,
                ):
                    start += 1
                if self._add(
                    (
                        interval.upper_value,
                        start_interval.upper_value,
                        not interval.upper_closed,
                        start_interval.upper_closed,
                    ),
                    start_value,
                ):
                    start += 1
        return start

    def _stop(self, interval):
        stop = self._intervals.bisect_right(interval)
        if 0 < stop <= len(self._intervals):
            stop -= 1
            stop_interval = self._intervals[stop]
            stop_value = self._mapping[stop_interval]
            if self._intervals[stop].during(interval, strict=False):
                del self._intervals[stop]
                del self._mapping[stop_interval]
            elif interval.overlaps(self._intervals[stop], strict=False):
                del self._intervals[stop]
                del self._mapping[stop_interval]
                self._add(
                    (
                        interval.upper_value,
                        stop_interval.upper_value,
                        not interval.upper_closed,
                        stop_interval.upper_closed,
                    ),
                    stop_value,
                )

        return stop

    def _add(self, key, value):
        interval = atomic.Atomic.from_tuple(key)
        if interval is not atomic.EMPTY:
            self._intervals.add(interval)
            self._mapping[interval] = value
            return True
        return False

    def _bisect_left(self, search) -> int:
        return self._intervals.bisect_left(search)

    def _update(self, intervals) -> None:
        self._intervals = SortedSet(intervals)
