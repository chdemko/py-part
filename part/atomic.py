"""Atomic values module."""

# pylint: disable=cyclic-import,too-many-lines

from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Union, Tuple, Any, Optional, Generic, TypeVar

import part
from part.utils import Singleton
from part.values import INFINITY, NegativeInfinity, PositiveInfinity  # type: ignore


class TotallyOrdered(ABC):
    """TotallyOrdered class."""

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        """Return self<other."""
        return NotImplemented

    @abstractmethod
    def __gt__(self, other: Any) -> bool:
        """Return self>other."""
        return NotImplemented

    @abstractmethod
    def __le__(self, other: Any) -> bool:
        """Return self<=other."""
        return NotImplemented

    @abstractmethod
    def __ge__(self, other: Any) -> bool:
        """Return self>=other."""
        return NotImplemented

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Return self!=other."""
        return NotImplemented

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Return self==other."""
        return NotImplemented


TO = TypeVar("TO", bound=TotallyOrdered)

IntervalTuple = Union[
    Tuple[Union[TO, NegativeInfinity, None], Union[TO, PositiveInfinity, None]],
    Tuple[
        Union[TO, NegativeInfinity, None],
        Union[TO, PositiveInfinity, None],
        Optional[bool],
    ],
    Tuple[
        Union[TO, NegativeInfinity, None],
        Union[TO, PositiveInfinity, None],
        Optional[bool],
        Optional[bool],
    ],
]


class Atomic(Generic[TO], ABC):
    """
    Atomic class.

    The :class:`Atomic` class represents an abstract version of two concrete classes:

    * :class:`Empty`
    * :class:`Interval`
    """

    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        """Return str(self)."""
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        """Return self==other."""
        return self is other or self.__compare(other)

    def __lt__(self, other) -> bool:
        """Return self<other."""
        return self.__compare(other)

    def __gt__(self, other) -> bool:
        """Return self>other."""
        return self.__compare(other)

    @abstractmethod
    def __hash__(self) -> int:
        """Return hash(self)."""
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
    def __or__(self, other) -> "part.FrozenIntervalSet[part.TO]":
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
    def __and__(self, other) -> "part.FrozenIntervalSet[part.TO]":
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
    def __sub__(self, other) -> "part.FrozenIntervalSet[part.TO]":
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
    def __xor__(self, other) -> "part.FrozenIntervalSet[part.TO]":
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
    def __invert__(self) -> "part.FrozenIntervalSet[part.TO]":
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
    def from_tuple(item: IntervalTuple[TO]):
        """
        Create an interval from a tuple.

        Arguments
        ---------
            item: :class:`IntervalTuple`
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
            >>> print(Atomic[int].from_tuple((10, 20)))
            [10;20)
            >>> print(Atomic[int].from_tuple((10, 20, True, None)))
            [10;20)
            >>> print(Atomic[int].from_tuple((10, 20, None, None)))
            (10;20)
            >>> print(Atomic[int].from_tuple((10, 20, None, True)))
            (10;20]
        """
        if len(item) == 1:
            return Interval[TO](
                lower_value=item[0],  # type: ignore
                upper_value=item[0],  # type: ignore
                upper_closed=True,
            )
        if len(item) == 2:
            return Interval[TO](lower_value=item[0], upper_value=item[1])
        if len(item) == 3:
            return Interval[TO](
                lower_value=item[0],
                upper_value=item[1],
                lower_closed=bool(item[2]) or None,  # type: ignore
            )
        if len(item) == 4:
            return Interval[TO](
                lower_value=item[0],
                upper_value=item[1],
                lower_closed=bool(item[2]) or None,  # type: ignore
                upper_closed=bool(item[3]) or None,  # type: ignore
            )
        raise TypeError("The argument is not a valid tuple")

    @staticmethod
    def from_value(value: Any):
        """
        Create an interval from any value.

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
            >>> print(Atomic[int].from_value(10))
            [10;10]
        """
        if isinstance(value, Empty):
            return value
        if isinstance(value, Interval):
            return value
        if isinstance(value, tuple):
            return Atomic.from_tuple(value)  # type: ignore
        return Atomic.from_tuple((value, value, True, True))

    @abstractmethod
    def meets(
        self, other: "Atomic[TO]", strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset meets the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *meets* strict?
            reverse: bool
                is the *meets* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def overlaps(
        self, other: "Atomic[TO]", strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset overlaps the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *overlap* strict?
            reverse: bool
                is the *overlaps* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def starts(
        self, other: "Atomic[TO]", strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset starts the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *starts* strict?
            reverse: bool
                is the *starts* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def during(
        self, other: "Atomic[TO]", strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset is during the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *during* strict?
            reverse: bool
                is the *during* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError

    @abstractmethod
    def finishes(
        self, other: "Atomic[TO]", strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset finishes the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *finishes* strict?
            reverse: bool
                is the *finishes* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`
        """
        raise NotImplementedError


class Empty(Generic[TO], Singleton, Atomic[TO]):
    """
    Empty set class.

    The :class:`Empty` class (which inherits from the :class:`Atomic` class) represent
    the empty set. There is only one instance of this class.
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Return str(self)."""
        return ""

    def __hash__(self) -> int:
        """Return hash(self)."""
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

    def __or__(self, other) -> "part.FrozenIntervalSet[part.TO]":
        """Return self|other."""
        if not isinstance(other, part.Atomic):
            return super().__or__(other)
        return part.FrozenIntervalSet[part.TO]([other])  # type: ignore

    def __and__(self, other) -> "part.FrozenIntervalSet[part.TO]":
        """Return self^other."""
        if not isinstance(other, part.Atomic):
            return super().__and__(other)
        return part.FrozenIntervalSet[part.TO]()

    def __sub__(self, other) -> "part.FrozenIntervalSet[part.TO]":
        """Return self-other."""
        if not isinstance(other, part.Atomic):
            return super().__sub__(other)
        return part.FrozenIntervalSet[part.TO]()

    def __xor__(self, other) -> "part.FrozenIntervalSet[part.TO]":
        """Return self^other."""
        if not isinstance(other, part.Atomic):
            return super().__xor__(other)
        return part.FrozenIntervalSet[part.TO]([other])  # type: ignore

    def __invert__(self) -> "part.FrozenIntervalSet[part.TO]":
        """Return ~self."""
        return part.FrozenIntervalSet[part.TO]([Interval[TO]()])  # type: ignore

    # pylint: disable=unused-argument,no-self-use
    def meets(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """See :meth:`Atomic.meets`."""
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        return False

    # pylint: disable=unused-argument,no-self-use
    def overlaps(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """See :meth:`Atomic.overlaps`."""
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        return False

    # pylint: disable=unused-argument,no-self-use
    def starts(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """See :meth:`Atomic.starts`."""
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        return False

    # pylint: disable=unused-argument,no-self-use
    def during(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """See :meth:`Atomic.during`."""
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        return False

    # pylint: disable=unused-argument,no-self-use
    def finishes(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """See :meth:`Atomic.finishes`."""
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        return False


class Mark(namedtuple("Mark", ["value", "type"])):
    """
    Mark class.

    The :class:`Mark` is used to represent a boundary in an :class:`Interval`. It
    contains two fields:

    * ``value`` which is the value
    * ``type`` which is an int representing the type of value:
      - 0 for a closed mark
      - -1 for an open upper mark
      - 1 for an open lower mark
    """

    def __str__(self) -> str:
        """Return str(self)."""
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


class Interval(Generic[TO], Atomic[TO]):
    """
    Interval class.

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
        lower_value: Optional[Union[TO, NegativeInfinity]] = None,
        upper_value: Optional[Union[TO, PositiveInfinity]] = None,
        lower_closed: Optional[bool] = True,
        upper_closed: Optional[bool] = None,
    ) -> Atomic[TO]:
        """
        Create an :class:`Atomic` instance.

        Keyword Arguments
        -----------------
            lower_value: :class:`TO <TotallyOrdered>`, optional
                Any python comparable object.
            upper_value: :class:`TO <TotallyOrdered>`, optional
                Any python comparable object.
            lower_closed: bool, optional
                A boolean value.
            upper_closed: bool, optional
                A boolean value.

        Returns
        -------
            :class:`Interval`
                if the arguments define a non-empty interval.
            :const:`Empty`
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

            >>> from part import Interval
            >>> a = Interval[int](lower_value=10, upper_value=0)
            >>> bool(a)
            False
        """
        if (
            lower_value is None
            or upper_value is None
            or lower_value <= upper_value
            or lower_value >= upper_value
        ):
            if lower_value is INFINITY:
                return Empty[TO]()  # type: ignore
            if upper_value is -INFINITY:
                return Empty[TO]()  # type: ignore
            if lower_value is None:
                return super().__new__(  # type: ignore
                    cls,
                    lower_value=lower_value,
                    upper_value=upper_value,
                    lower_closed=lower_closed,
                    upper_closed=upper_closed,
                )
            if upper_value is None:
                return super().__new__(  # type: ignore
                    cls,
                    lower_value=lower_value,
                    upper_value=upper_value,
                    lower_closed=lower_closed,
                    upper_closed=upper_closed,
                )

            if (
                lower_value > upper_value
                or lower_value == upper_value
                and not (lower_closed and upper_closed)
            ):  # type: ignore
                return Empty[TO]()  # type: ignore
            return super().__new__(  # type: ignore
                cls,
                lower_value=lower_value,
                upper_value=upper_value,
                lower_closed=lower_closed,
                upper_closed=upper_closed,
            )
        raise ValueError(f"{lower_value} must be comparable with {upper_value}")

    def __init__(
        self,
        lower_value: Optional[Union[TO, NegativeInfinity]] = None,
        upper_value: Optional[Union[TO, PositiveInfinity]] = None,
        lower_closed: Optional[bool] = True,
        upper_closed: Optional[bool] = None,
    ) -> None:
        """
        Initialize an :class:`Interval` instance.

        By default, an interval is closed to the left and open to the right.

        Keyword Arguments
        -----------------
            lower_value: :class:`TO <TotallyOrdered>`, optional
                Any python object.
            upper_value: :class:`TO <TotallyOrdered>`, optional
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
            >>> print(Interval[int](lower_value=10, upper_value=20))
            [10;20)
            >>> print(Interval[str](lower_value="abc", upper_value="def",
            ... upper_closed=True))
            ['abc';'def']
            >>> print(Interval[int](lower_closed=None, lower_value=10, upper_value=20))
            (10;20)
            >>> print(Interval[int]())
            (-inf;+inf)
        """
        if lower_value is None:
            lower_value = -INFINITY  # type: ignore
            lower_closed = False
        if upper_value is None:
            upper_value = INFINITY  # type: ignore
            upper_closed = False
        self._lower = Mark(value=lower_value, type=0 if lower_closed else 1)
        self._upper = Mark(value=upper_value, type=0 if upper_closed else -1)

    def __str__(self) -> str:
        """Return str(self)."""
        return (
            f"{'[' if self._lower.type == 0 else '('}"
            f"{repr(self._lower.value)};{repr(self._upper.value)}"
            f"{']' if self._upper.type == 0 else ')'}"
        )

    def __eq__(self, other) -> bool:
        """Return self==other."""
        if super().__eq__(other) is NotImplemented:
            return NotImplemented
        if not other:
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> a < Atomic[int].from_tuple((25, 30))
            True
        """
        if super().__eq__(other) is NotImplemented:
            return NotImplemented
        if not other:
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> a > Atomic[int].from_tuple((25, 30))
            False
        """
        if super().__eq__(other) is NotImplemented:
            return NotImplemented
        if not other:
            return False
        return self._lower > other.upper

    def __hash__(self) -> int:
        """Return hash(self)."""
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

    def __or__(self, other) -> "part.FrozenIntervalSet[part.TO]":
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> b = Atomic[int].from_tuple((15, 30))
            >>> c = Atomic[int].from_tuple((30, 40))
            >>> print(a | b)
            (10;30)
            >>> print(a | c)
            (10;20) | [30;40)
        """
        return part.FrozenIntervalSet[TO]([self, other])  # type: ignore

    def __and__(self, other) -> "part.FrozenIntervalSet[part.TO]":
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> b = Atomic[int].from_tuple((15, 30))
            >>> c = Atomic[int].from_tuple((30, 40))
            >>> print(a & b)
            [15;20)
            >>> print(a & c)
            <BLANKLINE>
        """
        if not isinstance(other, Atomic):
            return super().__and__(other)
        if not other:
            return part.FrozenIntervalSet[part.TO]()
        if self > other or self < other:
            return part.FrozenIntervalSet[part.TO]()
        result = Interval[TO]()
        result._lower = max(self._lower, other.lower)  # type: ignore
        result._upper = min(self._upper, other.upper)  # type: ignore
        return part.FrozenIntervalSet[TO]([result])  # type: ignore

    def __sub__(self, other) -> "part.FrozenIntervalSet[part.TO]":
        """
        Compute the difference of two intervals.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic value.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The difference between the interval and the *other*.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> b = Atomic[int].from_tuple((15, 30))
            >>> c = Atomic[int].from_tuple((30, 40))
            >>> print(a - b)
            (10;15)
            >>> print(a - c)
            (10;20)
        """
        if not isinstance(other, Atomic):
            return super().__sub__(other)
        return part.FrozenIntervalSet[part.TO](  # type: ignore
            [self]  # type: ignore
        ) - part.FrozenIntervalSet[part.TO](
            [other]  # type: ignore
        )

    def __xor__(self, other) -> "part.FrozenIntervalSet[part.TO]":
        """
        Compute the symmetric difference of two intervals.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic value.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The symmetric difference between the interval and the *other*.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> b = Atomic[int].from_tuple((15, 30))
            >>> c = Atomic[int].from_tuple((30, 40))
            >>> print(a ^ b)
            (10;15) | [20;30)
            >>> print(a ^ c)
            (10;20) | [30;40)
        """
        if not isinstance(other, part.Atomic):
            return super().__xor__(other)
        return part.FrozenIntervalSet[part.TO](  # type: ignore
            [self]  # type: ignore
        ) ^ part.FrozenIntervalSet[part.TO](
            [other]  # type: ignore
        )

    def __invert__(self) -> "part.FrozenIntervalSet[part.TO]":
        """
        Compute the complement of the interval.

        Returns
        -------
            :class:`FrozenIntervalSet`
                The complement of the interval.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> print(~a)
            (-inf;10] | [20;+inf)
        """
        return part.FrozenIntervalSet[part.TO](
            [
                Interval[TO].upper_limit(
                    value=self.lower_value, closed=not self.lower_closed
                ),
                Interval[TO].lower_limit(
                    value=self.upper_value, closed=not self.upper_closed
                ),
            ]
        )

    @staticmethod
    def upper_limit(
        value: Optional[Union[TO, PositiveInfinity]] = None,
        closed: Optional[bool] = None,
    ):
        """
        Create an interval from an upper limit.

        Arguments
        ---------
            value: :class:`TO <TotallyOrdered>`
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
            >>> print(Interval[int].upper_limit(value=10))
            (-inf;10)
            >>> print(Interval[int].upper_limit(value=10, closed=True))
            (-inf;10]
        """
        return Atomic[TO].from_tuple((-INFINITY, value, None, closed))  # type: ignore

    @staticmethod
    def lower_limit(
        value: Optional[Union[TO, NegativeInfinity]] = None,
        closed: Optional[bool] = True,
    ):
        """
        Create an interval from a lower limit.

        Arguments
        ---------
            value: :class:`TO <TotallyOrdered>`
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
            >>> print(Interval[int].lower_limit(value=10))
            [10;+inf)
            >>> print(Interval[int].lower_limit(value=10, closed=None))
            (10;+inf)
        """
        return Atomic.from_tuple((value, +INFINITY, closed, None))  # type: ignore

    def meets(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset meets the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *meets* strict?
            reverse: bool
                is the *meets* reversed?

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
            >>> a.meets(Atomic[int].from_tuple((20, 30)))
            False
            >>> a.meets(Atomic[int].from_tuple((20, 30)), strict=False)
            True
        """
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if reverse:
            return other.meets(self, strict=strict)
        if not other:
            return False
        if strict:
            return self._upper == other.lower
        return self._upper.near(other.lower)

    def overlaps(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset overlaps the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *overlaps* strict?
            reverse: bool
                is the *overlaps* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> a.overlaps(Atomic[int].from_tuple((15, 30)))
            True
        """
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if reverse:
            return other.overlaps(self, strict=strict)
        if not other:
            return False
        if strict:
            return self._lower < other.lower < self._upper < other.upper
        return self._lower <= other.lower <= self._upper <= other.upper

    def starts(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset starts the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *starts* strict?
            reverse: bool
                is the *starts* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> a.starts(Atomic[int].from_tuple((20, 40, None)))
            False
            >>> a.starts(Atomic[int].from_tuple((10, 40, None)), strict=False)
            True
        """
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if reverse:
            return other.starts(self, strict=strict)
        if not other:
            return False
        if strict:
            return self._lower == other.lower and self._upper < other.upper
        return self._lower.near(other.lower) and self._upper <= other.upper

    def during(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset is during the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *during* strict?
            reverse: bool
                is the *during* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> a.during(Atomic[int].from_tuple((0, 30)))
            True
        """
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if reverse:
            return other.during(self, strict=strict)
        if not other:
            return False
        if strict:
            return self._lower > other.lower and self._upper < other.upper
        return self._lower >= other.lower and self._upper <= other.upper

    def finishes(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool:
        """
        Return :data:`True <python:True>` if the subset finishes the *other*.

        Arguments
        ---------
            other: :class:`Atomic`
                Another atomic object.
            strict: bool
                is the *finishes* strict?
            reverse: bool
                is the *finishes* reversed?

        Raises
        ------
            NotImplementedError
                if the method is not implemented in the class.
            TypeError
                if *other* is not an instance of :class:`Atomic`

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> a.finishes(Atomic[int].from_tuple((0, 20)))
            True
        """
        if not isinstance(other, part.Atomic):
            raise TypeError(
                f"{other.__class__.__name__} argument must be an instance of Atomic"
            )
        if reverse:
            return other.finishes(self, strict=strict)
        if not other:
            return False
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> print(a.lower)
            10+
        """
        return self._lower

    @property
    def lower_value(self) -> TO:
        """
        Get the ``lower_value`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> print(a.upper)
            20-
        """
        return self._upper

    @property
    def upper_value(self) -> TO:
        """
        Get the ``lower_value`` property.

        Examples
        --------

            >>> from part import Atomic
            >>> a = Atomic[int].from_tuple((10, 20, None))
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
            >>> a = Atomic[int].from_tuple((10, 20, None))
            >>> print(a.upper_closed)
            None
        """
        return self._upper.type == 0 or None


IntervalValue = Union[TO, Interval[TO], IntervalTuple[TO]]

FULL: Interval = Interval()
"""
:const:`FULL` represents the full set.
"""
