"""Interval dictionaries module."""

# pylint: disable=too-many-lines

import bisect
import collections.abc
import itertools
from abc import ABCMeta, abstractmethod
from functools import reduce
from typing import (
    Union,
    Mapping,
    Iterable,
    Tuple,
    List,
    Optional,
    Iterator,
    Callable,
    Generic,
    MutableMapping,
    TypeVar,
)

# pylint: disable=import-error
from sortedcontainers import SortedSet, SortedList  # type: ignore

from part import atomic, sets

# pylint: disable=invalid-name
V = TypeVar("V")


# pylint: disable=too-many-ancestors
class IntervalDict(
    Generic[atomic.TO, V], Mapping[atomic.Interval[atomic.TO], V], metaclass=ABCMeta
):
    """
    The :class:`IntervalDict` abstract class can hold dict of disjoint sorted intervals.

    It implements the :class:`Mapping <python:typing.Mapping>` protocol. It is
    implemented in two concrete classes:

    * :class:`FrozenIntervalDict`
    * :class:`MutableIntervalDict`

    Note
    ----
        Les :math:`n` (or :math:`n_0`)  the number of intervals of the *self* variable
        and :math:`m` the number of intervals in the *other* variable. Let
        :math:`n_1, ... n_k` the number of intervals for methods with multiple
        arguments.

        The complexity in time of methods is estimated at (it has to be proven,
        see https://github.com/chdemko/py-part/issues/3):

        ============================  ===================================
        Methods                       Average case
        ============================  ===================================
        :meth:`__len__`               :math:`O(1)`
        :meth:`__iter__`              :math:`O(1)`
        :meth:`__contains__`          :math:`O(\\log(n))`
        :meth:`__getitem__`           :math:`O(\\log(n))` :math:`O(n)`
        :meth:`__or__`                :math:`O(m\\log(n+m))`
        :meth:`copy`                  :math:`O(n)`
        :meth:`select`                :math:`O(\\log(n))`
        :meth:`compress`              :math:`O(n)`
        ============================  ===================================

        The iteration using :meth:`__iter__` or :meth:`select` is in :math:`O(n)`.
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
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
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
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
            >>> len(a)
            3
        """
        return len(self._intervals)  # type: ignore

    def __iter__(self) -> Iterator[atomic.Interval[atomic.TO]]:
        """
        Return an iterator over the intervals.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
            >>> print(list(str(interval) for interval in a))
            ['[10;15)', '[20;25)', '[30;35)']
        """
        return iter(self._intervals)  # type: ignore

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

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
            >>> print(a)
            {'[10;15)': 1, '[20;25)': 2, '[30;35)': 3}
            >>> (10,13) in a
            True
            >>> (13,17) in a
            False
        """
        if not value:
            return True
        interval = atomic.Atomic.from_value(value)
        index = self._bisect_left(interval)
        if index < len(self._intervals):  # type: ignore
            other = self._intervals[index]  # type: ignore
            return interval.during(other, strict=False)
        return False

    def __getitem__(self, key: Union[atomic.IntervalValue[atomic.TO], slice]) -> V:
        """
        Return a value using either a slice or an interval value.

        Arguments
        ---------
            key: Union[IntervalValue, slice]
                The interval requested.

        Returns
        -------
            The found value or a new :class:`IntervalDict` if key is a slice.

        Raises
        ------
            KeyError
                If the *key* is out of range.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
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
            intervals = self._intervals.__class__()  # type: ignore
            mapping = {}
            for found in self.select(search, strict=False):
                value = self._mapping[found]
                interval = atomic.Interval()  # type: ignore
                interval._lower = max(found.lower, search.lower)
                interval._upper = min(found.upper, search.upper)
                intervals.append(interval)
                mapping[interval] = value
            # pylint: disable=too-many-function-args
            result = self.__class__()
            result._intervals = intervals
            result._mapping = mapping
            return result  # type: ignore
        interval = IntervalDict._interval(key)
        index = self._bisect_left(interval)
        if index < len(self._intervals):  # type: ignore
            other = self._intervals[index]  # type: ignore
            if interval.during(other, strict=False):
                return self._mapping[self._intervals[index]]  # type: ignore
        raise KeyError(str(key))

    def __or__(self, other) -> "IntervalDict[atomic.TO, V]":
        """
        Construct a new dictionary using self and the *other*.

        Arguments
        ---------
            other: :class:`IntervalDict`
                Another interval dict.

        Returns
        -------
            :class:`IntervalDict`
                The new :class:`IntervalDict`.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
            >>> print(a | FrozenIntervalDict[int, int]({(15, 22): 4}))
            {'[10;15)': 1, '[15;22)': 4, '[22;25)': 2, '[30;35)': 3}
        """
        if not isinstance(other, IntervalDict):
            return NotImplemented
        result = MutableIntervalDict[atomic.TO, V]()
        result.update(self, other)
        # pylint: disable=too-many-function-args
        return self.__class__(result)  # type: ignore

    def copy(self) -> "IntervalDict[atomic.TO, V]":
        """
        Return a shallow copy of the dictionary.

        Returns
        -------
            :class:`IntervalDict`
                A shallow copy of the dictionary.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
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
        self, value: atomic.IntervalValue[atomic.TO], strict: bool = True
    ) -> Iterator[atomic.Interval[atomic.TO]]:
        """
        Select all intervals that have a non-empty intersection with *value*.

        Arguments
        ---------
            value: :class:`IntervalValue`
                The value to search:

                * :class:`Atomic`
                * :class:`TO <TotallyOrdered>`
                * :class:`Tuple[TO, TO] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool]] <python:tuple>`
                * :class:`Tuple[TO, TO, Optional[bool], Optional[bool]] <python:tuple>`
            strict: bool
                Is the comparison strict?

        Returns
        -------
            :class:`Iterator[Interval]] <python:typing.Iterator>`
                An iterator over the selected items.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
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
        if not value:
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

    def compress(self) -> "IntervalDict[atomic.TO, V]":
        """
        Compress a dictionary.

        Returns
        -------
            :class:`IntervalDict`
                A new dictionary where all useless intervals have been removed.

        Examples
        --------

            >>> from part import FrozenIntervalDict
            >>> a = FrozenIntervalDict[int, int](
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
                    result._update_intervals(intervals)
                    result._mapping[current] = value
                    break
        return result

    @abstractmethod
    def _bisect_left(self, search):  #  pylint: disable=invalid-name
        raise NotImplementedError

    @abstractmethod
    def _update_intervals(self, intervals) -> None:
        raise NotImplementedError


# pylint: disable=too-few-public-methods
class FrozenIntervalDict(
    # pylint: disable=unsubscriptable-object
    IntervalDict[atomic.TO, V],
):
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
                Mapping[atomic.IntervalValue[atomic.TO], V],
                Iterable[Tuple[atomic.IntervalValue[atomic.TO], V]],
            ]
        ] = None,
    ) -> None:
        """
        Initialize a :class:`FrozenIntervalDict` instance.

        Arguments
        ---------
            iterable: :class:`Iterable <python:typing.Iterable>`
                An optional iterable that can be converted to a dictionary of (
                interval, value).
        """
        super().__init__()
        self._hash: Optional[int] = None
        other = MutableIntervalDict[atomic.TO, V](iterable)
        self._intervals: List[atomic.Interval] = list(other._intervals)  # type: ignore
        self._mapping = other._mapping

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

    def _update_intervals(self, intervals) -> None:
        self._intervals = intervals


# pylint: disable=too-many-ancestors, abstract-method
class MutableIntervalDict(
    # pylint: disable=unsubscriptable-object
    IntervalDict[atomic.TO, V],
    MutableMapping[atomic.Interval[atomic.TO], V],
):
    """
    Mutable Interval Dictionary class.

    The :class:`MutableIntervalDict` class (which inherits from the
    :class:`IntervalDict` class) is designed to hold mutable dict of disjoint sorted
    intervals.

    Note
    ----
        Les :math:`n` (or :math:`n_0`)  the number of intervals of the *self* variable
        and :math:`m` the number of intervals in the *other* variable. Let
        :math:`n_1, ... n_k` the number of intervals for methods with multiple
        arguments.

        The complexity in time of methods is:

        =========================  ====================================================
        Methods                    Average case
        =========================  ====================================================
        :meth:`__setitem__`        :math:`O(n)`
        :meth:`__delitem__`        :math:`O(n)`
        :meth:`__ior__`            :math:`O(m\\log(n+m))`
        :meth:`update`             :math:`O((\\sum_{i=1}^kn_i)\\log(\\sum_{i=0}^kn_i))`
        :meth:`clear`              :math:`O(1)`
        =========================  ====================================================
    """

    __slots__ = ("_default", "_operator", "_strict")

    def __init__(
        self,
        iterable: Optional[
            Union[
                IntervalDict[atomic.TO, V],
                Mapping[atomic.IntervalValue[atomic.TO], V],
                Iterable[Tuple[atomic.IntervalValue[atomic.TO], V]],
            ]
        ] = None,
        default: Optional[Callable[[], V]] = None,
        operator: Optional[Callable[[V, V], V]] = None,
        strict: Optional[bool] = True,
    ) -> None:
        """
        Initialize a :class:`MutableIntervalDict` instance.

        Arguments
        ---------
            iterable: :class:`Iterable <python:typing.Iterable>`
                An optional iterable that can be converted to a dictionary of (
                interval, value).

        Keyword arguments
        -----------------
            default: :class:`Callable[[], V] <python:typing.Callable>`, optional
                The default factory.
            operator: :class:`Callable[[V, V], V] <python:typing.Callable>`
                The operator function.
            strict: bool
                :data:`False <python:False>` if ``operator`` is a commutative and
                associative law on ``V``.

        Note
        ----

            If  ``operator`` is a commutative and associative law on ``V``,
            the complexity in time is much faster if ``strict`` is set to
            :data:`False <python:False>`.

        Examples
        --------

            >>> from part import MutableIntervalDict
            >>> a = MutableIntervalDict[int, set](
            ...     operator=lambda x, y: x | y,
            ...     strict=False
            ... )
            >>> a.update({(1, 10): {1}})
            >>> print(a)
            {'[1;10)': {1}}
            >>> a.update({(5, 20): {2}})
            >>> print(a)
            {'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2}}
            >>> a.update({(10, 30): {1}})
            >>> print(a)
            {'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {1, 2}, '[20;30)': {1}}
            >>> print(a.compress())
            {'[1;5)': {1}, '[5;20)': {1, 2}, '[20;30)': {1}}
        """
        super().__init__()
        self._default = default
        self._operator = operator
        self._strict = strict
        if isinstance(iterable, IntervalDict):
            self._mapping = iterable._mapping.copy()
            self._intervals = SortedSet(iterable._intervals)
        else:
            self._mapping = {}
            self._intervals: SortedSet = SortedSet()
            if isinstance(iterable, dict):
                self.update(*({key: value} for key, value in iterable.items()))
            elif iterable is not None:
                self.update(*({key: value} for key, value in iterable))  # type: ignore

    def __getitem__(self, key: Union[slice, atomic.IntervalValue[atomic.TO]]) -> V:
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

    def __setitem__(
        self, key: Union[slice, atomic.IntervalValue[atomic.TO]], value: V
    ) -> None:
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

            >>> from part import MutableIntervalDict
            >>> a = MutableIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
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
        interval = self._remove(key)
        if interval:
            self._intervals.add(interval)
            self._mapping[interval] = value

    def __delitem__(self, key: Union[slice, atomic.IntervalValue[atomic.TO]]) -> None:
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

            >>> from part import MutableIntervalDict
            >>> a = MutableIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3}
            ... )
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
        self._remove(key)

    def _remove(self, key):
        # pylint: disable=protected-access
        interval = IntervalDict._interval(key)
        if interval:
            start = self._start(interval)
            stop = self._stop(interval)
            for index in range(start, stop):
                del self._mapping[self._intervals[index]]
            del self._intervals[start:stop]
        return interval

    def _add(self, interval, value):
        if self._operator is None:
            self[interval] = value
        else:
            intervals = list(self.select(interval, strict=False))
            for another in ((interval & found)[0] for found in intervals):
                self[another] = self._operator(self[another], value)
            for another in sets.FrozenIntervalSet[atomic.TO](
                [interval]
            ) - sets.FrozenIntervalSet[atomic.TO](intervals):
                self[another] = value

    def __or__(self, other) -> "MutableIntervalDict[atomic.TO, V]":
        """
        Construct a new dictionary using self and the *other*.

        Arguments
        ---------
            other: :class:`IntervalDict`
                Another interval dict.

        Returns
        -------
            :class:`MutableIntervalDict`
                The new :class:`IntervalDict`.

        Examples
        --------

            >>> from part import MutableIntervalDict
            >>> a = MutableIntervalDict[int, int](
            ...     {(10, 15): 1, (20, 25): 2, (30, 35): 3},
            ...     operator=lambda x, y: x + y,
            ...     strict=False
            ... )
            >>> print(a | FrozenIntervalDict[int, int]({(15, 22): 4}))
            {'[10;15)': 1, '[15;20)': 4, '[20;22)': 6, '[22;25)': 2, '[30;35)': 3}
        """
        if not isinstance(other, IntervalDict):
            return NotImplemented
        result = self.__class__(
            self, default=self._default, operator=self._operator, strict=self._strict
        )
        result.update(other)
        return result

    def __ior__(self, other) -> "MutableIntervalDict[atomic.TO, V]":
        """
        Update self with the *other*.

        Arguments
        ---------
            other: :class:`IntervalDict`
                Another interval dict.

        Returns
        -------
            :class:`MutableIntervalDict`
                The updated :class:`MutableIntervalDict`.

        Examples
        --------

            >>> from part import MutableIntervalDict
            >>> a = MutableIntervalDict[int, int](
            ...     operator=lambda x, y: x + y,
            ...     strict=False
            ... )
            >>> a |= MutableIntervalDict[int, int]({(1, 10): 1})
            >>> print(a)
            {'[1;10)': 1}
            >>> a |= MutableIntervalDict[int, int]({(5, 20): 2})
            >>> print(a)
            {'[1;5)': 1, '[5;10)': 3, '[10;20)': 2}
            >>> a |= MutableIntervalDict[int, int]({(10, 30): 3})
            >>> print(a)
            {'[1;5)': 1, '[5;10)': 3, '[10;20)': 5, '[20;30)': 3}
        """
        if not isinstance(other, IntervalDict):
            return NotImplemented
        self.update(other)
        return self

    # pylint: disable=arguments-differ,signature-differs
    def update(  # type: ignore
        self,
        *args: Union[
            IntervalDict,
            Mapping[atomic.IntervalValue[atomic.TO], V],
            Iterable[Tuple[atomic.IntervalValue[atomic.TO], V]],
        ],
    ) -> None:
        """
        Update the dict.

        Arguments
        ---------
            *args: :class:`Iterable <python:typing.Iterable>`
                An iterable of :class:`IntervalDict` or valid iterable for an interval
                dictionary creation.

        Raises
        ------
            TypeError
                if an argument is not iterable.

        Note
        ----
            If the parameter ``strict`` used in the constructor is :data:`False
            <python:False>`, the complexity is in :math:`O(n\\,log(n)\\,k\\,\\lambda)`
            where:

            * :math:`n` is the length of ``*args``;
            * :math:`k` is the number of output intervals;
            * :math:`\\lambda` is the the cost of the ``operator`` parameter used in
              the constructor.

        Examples
        --------

            >>> from part import MutableIntervalDict
            >>> from operator import add
            >>> a = MutableIntervalDict[int, int](
            ...     operator=add,
            ...     default=lambda: 0,
            ... )
            >>> a.update({(1, 10): 1})
            >>> print(a)
            {'[1;10)': 1}
            >>> a.update(
            ...     FrozenIntervalDict[int, int]({(5, 20): 2}),
            ...     FrozenIntervalDict[int, int]({(10, 30): 3})
            ... )
            >>> print(a)
            {'[1;5)': 1, '[5;10)': 3, '[10;20)': 5, '[20;30)': 3}
            >>> a = MutableIntervalDict[int, set](
            ...     operator=lambda x, y: x | y,
            ...     strict=False
            ... )
            >>> a.update({(1, 10): {1}})
            >>> print(a)
            {'[1;10)': {1}}
            >>> a.update(
            ...     FrozenIntervalDict[int, set]({(5, 20): {2}}),
            ...     FrozenIntervalDict[int, set]({(10, 30): {3}})
            ... )
            >>> print(a)
            {'[1;5)': {1}, '[5;10)': {1, 2}, '[10;20)': {2, 3}, '[20;30)': {3}}
        """
        # TODO determine complexity
        strict = self._strict
        operator = self._operator
        if strict or operator is None:
            self._strict_update(*args)
        else:
            self._enhanced_update(*args)

    def _strict_update(
        self,
        *args: Union[
            IntervalDict,
            Mapping[atomic.IntervalValue[atomic.TO], V],
            Iterable[Tuple[atomic.IntervalValue[atomic.TO], V]],
        ],
    ) -> None:
        for other in args:
            if isinstance(other, collections.abc.Mapping):
                for key, value in other.items():
                    self._add(atomic.Atomic.from_value(key), value)
            elif isinstance(other, collections.abc.Iterable):
                for key, value in other:  # type: ignore
                    self._add(atomic.Atomic.from_value(key), value)
            else:
                raise TypeError(f"{type(other)} object is not iterable")

    # pylint: disable=protected-access
    @classmethod
    def _rest(cls, rest, cursors, index, element):
        if cursors[index] < len(element):
            interval = element._intervals[cursors[index]]
            value = element._mapping[interval]
            rest.add((interval.lower, interval.upper, index, value))

    # pylint: disable=protected-access
    def _create(self, *args):
        # Create a list of non empty IntervalDict
        elements = []
        for element in itertools.chain([self], args):
            if not isinstance(element, IntervalDict):
                element = FrozenIntervalDict(element)
            if element:
                elements.append(element)

        cursors = [0] * len(elements)

        current = SortedList()

        rest = SortedList()
        for index, element in enumerate(elements):
            self._rest(rest, cursors, index, element)

        return (elements, cursors, current, rest)

    # pylint: disable=too-many-arguments,protected-access
    @classmethod
    def _next(cls, upper, elements, cursors, current, rest):

        # Remove useless elements from current
        while current and current[0][0] == upper:
            (_, _, index, _) = current[0]
            del current[0]
            cursors[index] += 1
            element = elements[index]
            cls._rest(rest, cursors, index, element)

        if current or not rest:
            lower = upper.next()
        else:
            lower = rest[0][0]

        # Move elements from rest to current
        while rest and rest[0][0] == lower:
            (lower, upper, index, value) = rest[0]
            del rest[0]
            current.add((upper, lower, index, value))

        if current:
            upper = current[0][0]
        if rest:
            upper = min(upper, rest[0][0].prev())

        return (lower, upper)

    def _enhanced_update(
        self,
        *args: Union[
            IntervalDict,
            Mapping[atomic.IntervalValue[atomic.TO], V],
            Iterable[Tuple[atomic.IntervalValue[atomic.TO], V]],
        ],
    ) -> None:
        intervals = []
        mapping = {}

        (elements, cursors, current, rest) = self._create(*args)
        (lower, upper) = self._next(-atomic.INFINITY, elements, cursors, current, rest)

        while current:
            interval = atomic.Interval[atomic.TO](
                lower_value=lower.value,
                lower_closed=lower.type == 0,
                upper_value=upper.value,
                upper_closed=upper.type == 0,
            )
            value = reduce(
                self._operator, (value for (_, _, _, value) in current)  # type: ignore
            )
            intervals.append(interval)
            mapping[interval] = value
            (lower, upper) = self._next(upper, elements, cursors, current, rest)

        self._intervals = SortedSet(intervals)
        self._mapping = mapping

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
                if self._insert(
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
                if self._insert(
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
                if self._insert(
                    (
                        start_interval.lower_value,
                        interval.lower_value,
                        start_interval.lower_closed,
                        not interval.lower_closed,
                    ),
                    start_value,
                ):
                    start += 1
                if self._insert(
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
                self._insert(
                    (
                        interval.upper_value,
                        stop_interval.upper_value,
                        not interval.upper_closed,
                        stop_interval.upper_closed,
                    ),
                    stop_value,
                )

        return stop

    def _insert(self, key, value):
        interval = atomic.Atomic.from_tuple(key)
        if interval:
            self._intervals.add(interval)
            self._mapping[interval] = value
            return True
        return False

    def _bisect_left(self, search) -> int:
        return self._intervals.bisect_left(search)

    def _update_intervals(self, intervals) -> None:
        self._intervals = SortedSet(intervals)
