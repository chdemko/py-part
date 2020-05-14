from abc import abstractmethod, ABCMeta
from typing import (
    Optional,
    Any,
    Iterator,
    Union,
    Tuple,
    Iterable,
    KeysView,
    ItemsView,
    ValuesView,
    Callable,
    TypeVar,
    Generic,
    AbstractSet,
    MutableSet,
    Mapping,
    MutableMapping,
)

class PositiveInfinity:
    def __lt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __pos__(self) -> PositiveInfinity: ...
    def __neg__(self) -> NegativeInfinity: ...
    def __repr__(self) -> str: ...

class NegativeInfinity:
    def __lt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __pos__(self) -> NegativeInfinity: ...
    def __neg__(self) -> PositiveInfinity: ...
    def __repr__(self) -> str: ...

class TotallyOrdered(metaclass=ABCMeta):
    @abstractmethod
    def __lt__(self, other: Any) -> bool: ...
    @abstractmethod
    def __gt__(self, other: Any) -> bool: ...
    @abstractmethod
    def __le__(self, other: Any) -> bool: ...
    @abstractmethod
    def __ge__(self, other: Any) -> bool: ...
    @abstractmethod
    def __ne__(self, other: Any) -> bool: ...
    @abstractmethod
    def __eq__(self, other: Any) -> bool: ...

TO = TypeVar("TO", bound=TotallyOrdered)

INFINITY: Any = ...

class Atomic(Generic[TO]):
    @abstractmethod
    def __str__(self) -> str: ...
    @abstractmethod
    def __eq__(self, other) -> bool: ...
    @abstractmethod
    def __lt__(self, other) -> bool: ...
    @abstractmethod
    def __gt__(self, other) -> bool: ...
    @abstractmethod
    def __hash__(self) -> int: ...
    @abstractmethod
    def __bool__(self) -> bool: ...
    @abstractmethod
    def __or__(self, other) -> FrozenIntervalSet[TO]: ...
    @abstractmethod
    def __and__(self, other) -> FrozenIntervalSet[TO]: ...
    @abstractmethod
    def __invert__(self) -> FrozenIntervalSet[TO]: ...
    @abstractmethod
    def meets(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    @abstractmethod
    def overlaps(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    @abstractmethod
    def starts(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    @abstractmethod
    def during(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    @abstractmethod
    def finishes(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...

class Empty(Generic[TO], Atomic[TO]):
    def __str__(self) -> str: ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __or__(self, other) -> FrozenIntervalSet[TO]: ...
    def __and__(self, other) -> FrozenIntervalSet[TO]: ...
    def __invert__(self) -> FrozenIntervalSet[TO]: ...
    def meets(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def overlaps(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def starts(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def during(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def finishes(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...

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

class Mark:
    def __str__(self) -> str: ...
    def near(self, other: Mark) -> bool: ...

class Interval(Generic[TO], Atomic[TO]):
    def __init__(
        self,
        lower_value: Optional[Union[TO, NegativeInfinity]] = None,
        upper_value: Optional[Union[TO, PositiveInfinity]] = None,
        left: bool = True,
        right: bool = False,
    ) -> None: ...
    def __str__(self) -> str: ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __or__(self, other) -> FrozenIntervalSet[TO]: ...
    def __and__(self, other) -> FrozenIntervalSet[TO]: ...
    def __invert__(self) -> FrozenIntervalSet[TO]: ...
    def meets(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def overlaps(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def starts(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def during(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    def finishes(
        self, other: Atomic[TO], strict: bool = True, reverse: bool = False
    ) -> bool: ...
    @staticmethod
    def from_tuple(item: IntervalTuple[TO]) -> Atomic[TO]: ...
    @staticmethod
    def from_value(value: TO) -> Atomic[TO]: ...
    @staticmethod
    def upper_limit(
        value: Optional[TO] = None, closed: Optional[bool] = None
    ) -> Interval[TO]: ...
    @staticmethod
    def lower_limit(
        value: Optional[TO] = None, closed: Optional[bool] = True
    ) -> Interval[TO]: ...
    @property
    def lower(self) -> Mark: ...
    @property
    def lower_value(self) -> TO: ...
    @property
    def lower_closed(self) -> bool: ...
    @property
    def upper(self) -> Mark: ...
    @property
    def upper_value(self) -> TO: ...
    @property
    def upper_closed(self) -> bool: ...

IntervalValue = Union[TO, Interval[TO], IntervalTuple[TO]]

class IntervalSet(Generic[TO], AbstractSet[Interval[TO]], metaclass=ABCMeta):
    def __str__(self) -> str: ...
    def __eq__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index) -> Interval[TO]: ...
    def __iter__(self) -> Iterator[Interval[TO]]: ...
    def __and__(self, other) -> IntervalSet[TO]: ...
    def __or__(self, other) -> IntervalSet[TO]: ...
    def __sub__(self, other) -> IntervalSet[TO]: ...
    def __xor__(self, other) -> IntervalSet[TO]: ...
    def __invert__(self) -> IntervalSet[TO]: ...
    def __reversed__(self) -> Iterator[Interval[TO]]: ...
    def isdisjoint(self, other: Iterable[IntervalValue[TO]]) -> bool: ...
    def issubset(self, other: Iterable[IntervalValue[TO]]) -> bool: ...
    def issuperset(self, other: Iterable[IntervalValue[TO]]) -> bool: ...
    def intersection(self, *args: Iterable[IntervalValue[TO]]) -> IntervalSet[TO]: ...
    def union(self, *args: Iterable[IntervalValue[TO]]) -> IntervalSet[TO]: ...
    def difference(self, *args: Iterable[IntervalValue[TO]]) -> IntervalSet[TO]: ...
    def symmetric_difference(
        self, other: Iterable[IntervalValue[TO]]
    ) -> IntervalSet[TO]: ...
    def copy(self) -> IntervalSet[TO]: ...
    def select(
        self, value: IntervalValue[TO], strict: bool = True
    ) -> Iterator[Interval[TO]]: ...

class FrozenIntervalSet(Generic[TO], IntervalSet[TO]):
    def __init__(
        self, iterable: Optional[Iterable[IntervalValue[TO]]] = None
    ) -> None: ...
    def __hash__(self) -> int: ...
    def __contains__(self, item) -> bool: ...

class MutableIntervalSet(Generic[TO], IntervalSet[TO], MutableSet[Interval[TO]]):
    def __init__(
        self, iterable: Optional[Iterable[IntervalValue[TO]]] = None
    ) -> None: ...
    def __contains__(self, item) -> bool: ...
    def __ior__(self, other) -> MutableIntervalSet[TO]: ...  # type: ignore
    def __iand__(self, other) -> MutableIntervalSet[TO]: ...
    def __isub__(self, other) -> MutableIntervalSet[TO]: ...
    def __ixor__(self, other) -> MutableIntervalSet[TO]: ...  # type: ignore
    def update(self, *args: Iterable[IntervalValue[TO]]) -> None: ...
    def intersection_update(self, *args: Iterable[IntervalValue[TO]]) -> None: ...
    def difference_update(self, *args: Iterable[IntervalValue[TO]]) -> None: ...
    def symmetric_difference_update(
        self, other: Iterable[IntervalValue[TO]]
    ) -> None: ...
    def add(self, value: IntervalValue[TO]) -> None: ...
    def remove(self, value: IntervalValue[TO]) -> None: ...
    def discard(self, value: IntervalValue[TO]) -> None: ...
    def pop(self) -> Interval[TO]: ...
    def clear(self) -> None: ...

V = TypeVar("V")

class IntervalDict(Generic[TO, V], Mapping[Interval[TO], V], metaclass=ABCMeta):
    def __str__(self) -> str: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Interval[TO]]: ...
    def __getitem__(self, key: Union[slice, IntervalValue[TO]]) -> V: ...
    def __contains__(self, key: Any) -> bool: ...
    def __eq__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...
    def __or__(self, other) -> IntervalDict[TO, V]: ...
    def keys(self) -> KeysView[Interval[TO]]: ...
    def items(self) -> ItemsView[Interval[TO], V]: ...
    def values(self) -> ValuesView[V]: ...
    def get(self, key: IntervalValue[TO], default=None) -> V: ...
    def copy(self) -> IntervalDict[TO, V]: ...
    def select(
        self, value: IntervalValue[TO], strict: bool = True
    ) -> Iterator[Interval[TO]]: ...

class FrozenIntervalDict(Generic[TO, V], IntervalDict[TO, V]):
    def __init__(
        self,
        iterable: Optional[
            Union[Mapping, Iterable[Tuple[IntervalValue[TO], V]]]
        ] = None,
    ) -> None: ...

class MutableIntervalDict(
    Generic[TO, V], IntervalDict[TO, V], MutableMapping[Interval[TO], V]
):
    def __init__(
        self,
        iterable: Optional[
            Union[Mapping, Iterable[Tuple[IntervalValue[TO], V]]]
        ] = None,
        update: Optional[Callable[[Any, Any], Any]] = None,
    ) -> None: ...
    def __setitem__(self, key: Union[slice, IntervalValue[TO]], value) -> None: ...
    def __delitem__(self, key: Union[slice, IntervalValue[TO]]) -> None: ...
    def __ior__(self, other) -> MutableIntervalDict[TO, V]: ...
    def update(  # type: ignore
        self,
        *args: Union[
            IntervalDict[TO, V],
            Mapping[IntervalValue[TO], V],
            Iterable[Tuple[IntervalValue[TO], V]],
        ],
        operator: Optional[Callable[[Any, Any], Any]] = None,
        **kwargs
    ) -> None: ...
