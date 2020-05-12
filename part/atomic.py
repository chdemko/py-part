# pylint: disable=missing-module-docstring,cyclic-import,too-many-lines

from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Union, Tuple, Any, Optional

import part
from part.utils import Singleton
from part.values import INFINITY  # type: ignore


IntervalTuple = Union[
    Tuple[Any, Any],
    Tuple[Any, Any, Optional[bool]],
    Tuple[Any, Any, Optional[bool], Optional[bool]],
]


class Atomic(ABC):
    """
    The :class:`Atomic` class represents an abstract version of two concrete classes:

    * :class:`Empty`
    * :class:`Interval`
    """

    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        """
        Return self==other.
        """
        return self is other or self.__compare(other)

    def __lt__(self, other) -> bool:
        """
        Return self<other.
        """
        return self.__compare(other)

    def __gt__(self, other) -> bool:
        """
        Return self>other.
        """
        return self.__compare(other)

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __bool__(self) -> bool:
        """
        Return bool(self).

        Returns
        -------
            :data:`True <python:True>`
                If the subset is non empty.
            :data:`False <python:False>`
                Otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def __or__(self, other) -> "part.FrozenIntervalSet":
        """
        Return the union of self with *other*.

        Arguments
        ---------
            other: :class:`Atomic`, tuple
                Another atomic subset.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The union of self and *other*.
        """
        return NotImplemented

    @abstractmethod
    def __and__(self, other) -> "part.FrozenIntervalSet":
        """
        Return the intersection of self with *other*.

        Arguments
        ---------
            other: :class:`Atomic`, tuple
                Another atomic subset.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The intersection of self and *other*.
        """
        return NotImplemented

    @abstractmethod
    def __sub__(self, other) -> "part.FrozenIntervalSet":
        """
        Return the difference of self with *other*.

        Arguments
        ---------
            other: :class:`Atomic`, tuple
                Another atomic subset.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The difference of self and *other*.
        """
        return NotImplemented

    @abstractmethod
    def __xor__(self, other) -> "part.FrozenIntervalSet":
        """
        Return the symmetric difference of self with *other*.

        Arguments
        ---------
            other: :class:`Atomic`, tuple
                Another atomic subset.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The symmetric difference of self and *other*.
        """
        return NotImplemented

    @abstractmethod
    def __invert__(self) -> "part.FrozenIntervalSet":
        """
        Return the complement of self.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The complement of self.
        """
        raise NotImplementedError

    @staticmethod
    def __compare(other) -> bool:
        if not isinstance(other, Atomic):
            return NotImplemented
        return False

    @staticmethod
    def _compare(other) -> bool:
        if Atomic.__compare(other) is NotImplemented:
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        return False

    @staticmethod
    def from_tuple(item: IntervalTuple):
        """
        Creates an interval from a tuple

        Arguments
        ---------
            item: \
                    :class:`Tuple[Any, Any] <python:tuple>`, \
                    :class:`Tuple[Any, Any, Optional[bool]]  <python:tuple>`, \
                    :class:`Tuple[Any, Any, Optional[bool], Optional[bool]] \
                        <python:tuple>`
                The tuple to transform:

                * a pair ``<a,b>`` designates an interval closed on the left and open on
                  the right;
                * a triple ``<a,b,bool>`` designates an interval open/closed on the left
                  and open on the right;
                * a quadruplet ``<a,b,bool,bool>`` designates an interval open/closed on
                  the left and open/closed on the right.

        Returns
        -------
            :class:`Interval`
                The tuple transformed into an interval.
            :class:`Empty`
                If the interval is empty

        Examples
        --------

            >>> from part import Atomic
            >>> print(Atomic.from_tuple((10, 20)))
            [10;20)
            >>> print(Atomic.from_tuple((10, 20, True, None)))
            [10;20)
            >>> print(Atomic.from_tuple((10, 20, None, None)))
            (10;20)
            >>> print(Atomic.from_tuple((10, 20, None, True)))
            (10;20]
        """
        if len(item) == 1:
            return Interval(lower_value=item[0], upper_value=item[0], upper_closed=True)
        if len(item) == 2:
            return Interval(lower_value=item[0], upper_value=item[1])
        if len(item) == 3:
            return Interval(
                lower_value=item[0],
                upper_value=item[1],
                lower_closed=bool(item[2]) or None,  # type: ignore
            )
        if len(item) == 4:
            return Interval(
                lower_value=item[0],
                upper_value=item[1],
                lower_closed=bool(item[2]) or None,  # type: ignore
                upper_closed=bool(item[3]) or None,  # type: ignore
            )
        raise TypeError("The argument is not a valid tuple")

    @staticmethod
    def from_value(value: Any):
        """
        Creates an interval from any value

        Arguments
        ---------
            value: object
                The value to transform.

        Returns
        -------
            :class:`Interval`
                The value transformed into an interval containing one value.

        Examples
        --------

            >>> from part import Atomic
            >>> print(Atomic.from_value(10))
            [10;10]
        """
        if value is EMPTY:
            return EMPTY
        if isinstance(value, Interval):
            return value
        if isinstance(value, tuple):
            return Atomic.from_tuple(value)  # type: ignore
        return Atomic.from_tuple((value, value, True, True))

    @abstractmethod
    def meets(self, other: "Atomic", strict: bool = True) -> bool:
        """
        The :meth:`meets` method return :data:`True <python:True>` if the subset
        meets the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the meet strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def overlaps(self, other: "Atomic", strict: bool = True) -> bool:
        """
        The :meth:`overlaps` method return :data:`True <python:True>` if the subset
        overlaps the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the overlap strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def starts(self, other: "Atomic", strict: bool = True) -> bool:
        """
        The :meth:`starts` method return :data:`True <python:True>` if the subset
        starts the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the start strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def during(self, other: "Atomic", strict: bool = True) -> bool:
        """
        The :meth:`during` method return :data:`True <python:True>` if the subset
        is during the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the during strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def finishes(self, other: "Atomic", strict: bool = True) -> bool:
        """
        The :meth:`finishes` method return :data:`True <python:True>` if the subset
        finishes the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the finish strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError


class Empty(Singleton, Atomic):
    """
    The :class:`Empty` class (which inherits from the :class:`Atomic` class) represent
    the empty set. There is only one instance of this class called
    :const:`EMPTY <Empty>`.
    """

    __slots__ = ()

    def __str__(self) -> str:
        return ""

    def __hash__(self) -> int:
        return id(self)

    def __bool__(self) -> bool:
        """
        Return bool(self).

        Returns
        -------
            :data:`False <python:False>`
                An empty set is always :data:`False <python:False>`.
        """
        return False

    def __or__(self, other) -> "part.FrozenIntervalSet":
        if not isinstance(other, part.Atomic):
            return super().__or__(other)
        return part.FrozenIntervalSet([other])  # type: ignore

    def __and__(self, other) -> "part.FrozenIntervalSet":
        if not isinstance(other, part.Atomic):
            return super().__and__(other)
        return part.FrozenIntervalSet()

    def __sub__(self, other) -> "part.FrozenIntervalSet":
        if not isinstance(other, part.Atomic):
            return super().__sub__(other)
        return part.FrozenIntervalSet()

    def __xor__(self, other) -> "part.FrozenIntervalSet":
        if not isinstance(other, part.Atomic):
            return super().__xor__(other)
        return part.FrozenIntervalSet([other])  # type: ignore

    def __invert__(self) -> "part.FrozenIntervalSet":
        """See :meth:`Atomic.__invert__`."""
        return part.FrozenIntervalSet([FULL])  # type: ignore

    def meets(self, other: Atomic, strict: bool = True) -> bool:
        return Atomic._compare(other)

    def overlaps(self, other: Atomic, strict: bool = True) -> bool:
        return Atomic._compare(other)

    def starts(self, other: Atomic, strict: bool = True) -> bool:
        return Atomic._compare(other)

    def during(self, other: Atomic, strict: bool = True) -> bool:
        return Atomic._compare(other)

    def finishes(self, other: Atomic, strict: bool = True) -> bool:
        return Atomic._compare(other)


EMPTY = Empty()
"""
:ivar:`EMPTY` represents the empty set.
"""


class Mark(namedtuple("Mark", ["value", "type"])):
    """
    The :class:`Mark` is used to represent a boundary in an :class:`Interval`. It
    contains two fields:

    * ``value`` which is the value
    * ``type`` which is an int representing the type of value:
      - 0 for a closed mark
      - -1 for an open upper mark
      - 1 for an open lower mark
    """

    def __str__(self) -> str:
        return (
            f"{self.value}{'+' if self.type == 1 else '-' if self.type == -1 else ''}"
        )

    def near(self, other: "Mark"):
        """
        Return :data:`True <python:True>` if the value is near the *other*.

        Arguments
        ---------
            other:
                Another :class:`Mark`


        Returns
        -------
            :data:`True <python:True>`
                if the value is near the *other*,
            :data:`False <python:False>`
                otherwise.
        """
        return self.value == other.value and (
            self.type == 0 or other.type == 0 or self.type == other.type
        )


class Interval(Atomic):
    """
    The :class:`Interval` class (which inherits from the :class:`Atomic` class) is
    designed to hold range values. `Allen's interval
    algebra <https://en.wikipedia.org/wiki/Allen's_interval_algebra>`_ has been
    implemented.

    An interval can hold any type of value that implements a total order.

    Each bound of the interval can be open or closed.
    """

    __slots__ = ("_lower", "_upper")

    def __new__(  # type: ignore
        cls,
        lower_value: Optional[Any] = None,
        upper_value: Optional[Any] = None,
        lower_closed: Optional[bool] = True,
        upper_closed: Optional[bool] = None,
    ) -> Atomic:
        """
        Creates an :class:`Atomic` instance.

        Keyword Arguments
        -----------------
            lower_value: object, optional
                Any python object.
            upper_value: object, optional
                Any python object.
            lower_closed: bool, optional
                A boolean value.
            upper_closed: bool, optional
                A boolean value.

        Returns
        -------
            :class:`Interval`
                if the arguments define a non-empty interval.
            :const:`EMPTY  <Empty>`
                otherwise.

        Raises
        ------
            ValueError
                If ``lower_value`` is not comparable with ``upper_value``.

        See also
        --------

            __init__: For interval initialization.

        Examples
        --------

            >>> from part import Interval, EMPTY
            >>> a = Interval(lower_value=10, upper_value=0)
            >>> a is EMPTY
            True
        """
        if (
            lower_value is None
            or upper_value is None
            or lower_value <= upper_value
            or lower_value >= upper_value
        ):
            if lower_value is INFINITY:
                return EMPTY  # type: ignore
            if upper_value is -INFINITY:
                return EMPTY  # type: ignore
            if lower_value is None:
                return super().__new__(cls)
            if upper_value is None:
                return super().__new__(cls)

            if (
                lower_value > upper_value
                or lower_value == upper_value
                and not (lower_closed and upper_closed)
            ):  # type: ignore
                return EMPTY  # type: ignore
            return super().__new__(cls)
        raise ValueError(f"{lower_value} must be comparable with {upper_value}")

    def __init__(
        self,
        lower_value: Optional[Any] = None,
        upper_value: Optional[Any] = None,
        lower_closed: Optional[bool] = True,
        upper_closed: Optional[bool] = None,
    ) -> None:
        """
        Initialize an :class:`Interval` instance. By default, an interval is closed
        to the left and open to the right.

        Keyword Arguments
        -----------------
            lower_value: object, optional
                Any python object.
            upper_value: object, optional
                Any python object.
            lower_closed: bool, optional
                A boolean value.
            upper_closed: bool, optional
                A boolean value.

        See also
        --------

            __new__: For detection of empty interval creation.

        Examples
        --------
            >>> from part import Interval
            >>> print(Interval(lower_value=10, upper_value=20))
            [10;20)
            >>> print(Interval(lower_value="abc", upper_value="def", upper_closed=True))
            ['abc';'def']
            >>> print(Interval(lower_closed=None, lower_value=10, upper_value=20))
            (10;20)
            >>> print(Interval())
            (-inf;+inf)
        """
        if lower_value is None:
            lower_value = -INFINITY
            lower_closed = False
        if upper_value is None:
            upper_value = INFINITY  # type: ignore
            upper_closed = False
        self._lower = Mark(value=lower_value, type=0 if lower_closed else 1)
        self._upper = Mark(value=upper_value, type=0 if upper_closed else -1)

    def __str__(self) -> str:
        """
        Return str(self).
        """
        return (
            f"{'[' if self._lower.type == 0 else '('}"
            f"{repr(self._lower.value)};{repr(self._upper.value)}"
            f"{']' if self._upper.type == 0 else ')'}"
        )

    def __eq__(self, other) -> bool:
        """
        Return self==other.
        """
        if super().__eq__(other) is NotImplemented:
            return NotImplemented
        if other is EMPTY:
            return False
        return self._lower == other.lower and self._upper == other.upper

    def __lt__(self, other) -> bool:
        """
        Comparison using Allen's algebra.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic value.

        Returns
        -------
            :data:`True <python:True>`
                if the interval is lesser than the *other*.
            :data:`False <python:False>`
                otherwise.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a < Atomic.from_tuple((25, 30))
            True
        """
        if super().__eq__(other) is NotImplemented:
            return NotImplemented
        if other is EMPTY:
            return False
        return self._upper < other.lower

    def __gt__(self, other) -> bool:
        """
        Comparison using Allen's algebra.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic value.

        Returns
        -------
            :data:`True <python:True>`
                if the interval is greater than the *other*.
            :data:`False <python:False>`
                otherwise.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a > Atomic.from_tuple((25, 30))
            False
        """
        if super().__eq__(other) is NotImplemented:
            return NotImplemented
        if other is EMPTY:
            return False
        return other is not EMPTY and self._lower > other.upper

    def __hash__(self) -> int:
        return hash((self._lower, self._upper))

    def __bool__(self) -> bool:
        """
        Return bool(self).

        Returns
        -------
            :data:`True <python:True>`
                An interval is always :data:`True <python:True>`.
        """
        return True

    def __or__(self, other) -> "part.FrozenIntervalSet":
        """
        Compute the union of two intervals.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic value.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The union of the interval and the *other*.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> b = Atomic.from_tuple((15, 30))
            >>> c = Atomic.from_tuple((30, 40))
            >>> print(a | b)
            (10;30)
            >>> print(a | c)
            (10;20) | [30;40)
        """
        return part.FrozenIntervalSet([self, other])  # type: ignore

    def __and__(self, other) -> "part.FrozenIntervalSet":
        """
        Compute the intersection of two intervals.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic value.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The intersection of the interval and the *other*.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> b = Atomic.from_tuple((15, 30))
            >>> c = Atomic.from_tuple((30, 40))
            >>> print(a & b)
            [15;20)
            >>> print(a & c)
            <BLANKLINE>
        """
        if other is EMPTY:
            return part.FrozenIntervalSet()
        if not isinstance(other, Interval):
            return super().__and__(other)
        if self > other or self < other:
            return part.FrozenIntervalSet()
        result = Interval()
        result._lower = max(self._lower, other.lower)
        result._upper = min(self._upper, other.upper)
        return part.FrozenIntervalSet([result])  # type: ignore

    def __sub__(self, other) -> "part.FrozenIntervalSet":
        """
        Return self-other.
        """
        if not isinstance(other, Atomic):
            return super().__sub__(other)
        return part.FrozenIntervalSet(  # type: ignore
            [self]  # type: ignore
        ) - part.FrozenIntervalSet(
            [other]  # type: ignore
        )

    def __xor__(self, other) -> "part.FrozenIntervalSet":
        if not isinstance(other, part.Atomic):
            return super().__xor__(other)
        return part.FrozenIntervalSet(  # type: ignore
            [self]  # type: ignore
        ) ^ part.FrozenIntervalSet(
            [other]  # type: ignore
        )

    def __invert__(self) -> "part.FrozenIntervalSet":
        """
        Compute the complement of the interval.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The complement of the interval.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(~a)
            (-inf;10] | [20;+inf)
        """
        return part.FrozenIntervalSet(
            [
                Interval.upper_limit(
                    value=self.lower_value, closed=not self.lower_closed
                ),
                Interval.lower_limit(
                    value=self.upper_value, closed=not self.upper_closed
                ),
            ]
        )

    @staticmethod
    def upper_limit(value: Optional[Any] = None, closed: Optional[bool] = None):
        """
        Creates an interval from an upper limit.

        Arguments
        ---------
            value: object
                The upper limit.

            closed: bool
                Is the interval closed?

        Returns
        -------
            :class:`Interval`
                An interval with an upper limit.

        Examples
        --------

            >>> from part import Interval
            >>> print(Interval.upper_limit(value=10))
            (-inf;10)
            >>> print(Interval.upper_limit(value=10, closed=True))
            (-inf;10]
        """
        return Atomic.from_tuple((-INFINITY, value, None, closed))

    @staticmethod
    def lower_limit(value: Optional[Any] = None, closed: Optional[bool] = True):
        """
        Creates an interval from a lower limit.

        Arguments
        ---------
            value: object
                The lower limit.

            closed: bool
                Is the interval closed?

        Returns
        -------
            :class:`Interval`
                An interval with a lower limit.

        Examples
        --------

            >>> from part import Interval
            >>> print(Interval.lower_limit(value=10))
            [10;+inf)
            >>> print(Interval.lower_limit(value=10, closed=None))
            (10;+inf)
        """
        return Atomic.from_tuple((value, +INFINITY, closed, None))

    def meets(self, other: Atomic, strict: bool = True) -> bool:
        """
        The :meth:`meets` method return :data:`True <python:True>` if the subset
        meets the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the meet strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a.meets(Atomic.from_tuple((20, 30)))
            False
            >>> a.meets(Atomic.from_tuple((20, 30)), strict=False)
            True
        """
        if other is EMPTY:
            return False
        if not isinstance(other, Interval):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if strict:
            return self._upper == other.lower
        return self._upper.near(other.lower)

    def overlaps(self, other: Atomic, strict: bool = True) -> bool:
        """
        The :meth:`overlaps` method return :data:`True <python:True>` if the subset
        overlaps the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the overlap strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a.overlaps(Atomic.from_tuple((15, 30)))
            True
        """
        if other is EMPTY:
            return False
        if not isinstance(other, Interval):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if strict:
            return self._lower < other.lower < self._upper < other.upper
        return self._lower <= other.lower <= self._upper <= other.upper

    def starts(self, other: Atomic, strict: bool = True) -> bool:
        """
        The :meth:`starts` method return :data:`True <python:True>` if the subset
        starts the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the start strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a.starts(Atomic.from_tuple((20, 40, None)))
            False
            >>> a.starts(Atomic.from_tuple((10, 40, None)), strict=False)
            True
        """
        if other is EMPTY:
            return False
        if not isinstance(other, Interval):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if strict:
            return self._lower == other.lower and self._upper < other.upper
        return self._lower.near(other.lower) and self._upper <= other.upper

    def during(self, other: Atomic, strict: bool = True) -> bool:
        """
        The :meth:`during` method return :data:`True <python:True>` if the subset
        is during the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the during strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a.during(Atomic.from_tuple((0, 30)))
            True
        """
        if other is EMPTY:
            return False
        if not isinstance(other, Interval):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if strict:
            return self._lower > other.lower and self._upper < other.upper
        return self._lower >= other.lower and self._upper <= other.upper

    def finishes(self, other: Atomic, strict: bool = True) -> bool:
        """
        The :meth:`finishes` method return :data:`True <python:True>` if the subset
        finishes the *other*.

        Arguments
        ---------
            other: object
                Any python value
            strict: bool
                is the finish strict?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> a.finishes(Atomic.from_tuple((0, 20)))
            True
        """
        if other is EMPTY:
            return False
        if not isinstance(other, Interval):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if strict:
            return self._lower > other.lower and self._upper == other.upper
        return self._lower >= other.lower and self._upper.near(other.upper)

    @property
    def lower(self) -> Mark:
        """
        Get the ``lower`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(a.lower)
            10+
        """
        return self._lower

    @property
    def lower_value(self) -> Any:
        """
        Get the ``lower_value`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(a.lower_value)
            10
        """
        return self._lower.value

    @property
    def lower_closed(self) -> Optional[bool]:
        """
        Get the ``lower_closed`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(a.lower_closed)
            None
        """
        return self._lower.type == 0 or None

    @property
    def upper(self) -> Mark:
        """
        Get the ``upper`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(a.upper)
            20-
        """
        return self._upper

    @property
    def upper_value(self) -> Any:
        """
        Get the ``lower_value`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(a.upper_value)
            20
        """
        return self._upper.value

    @property
    def upper_closed(self) -> Optional[bool]:
        """
        Get the ``upper_closed`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic.from_tuple((10, 20, None))
            >>> print(a.upper_closed)
            None
        """
        return self._upper.type == 0 or None


IntervalValue = Union[Interval, IntervalTuple]

FULL: Interval = Interval()
"""
:const:`FULL` represents the full set.
"""
