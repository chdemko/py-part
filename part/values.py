# pylint: disable=missing-module-docstring

# noinspection Mypy
from .utils import Singleton


class PositiveInfinity(Singleton):
    """
    The :class:`PositiveInfinity` represents the positive infinity value. It exists
    only one instance of this class called :const:`INFINITY`.
    """

    __slots__ = ()

    def __lt__(self, _) -> bool:
        return False

    def __le__(self, other) -> bool:
        return self is other

    def __gt__(self, other) -> bool:
        return self is not other

    def __ge__(self, _) -> bool:
        return True

    def __pos__(self) -> "PositiveInfinity":
        return self

    def __neg__(self) -> "NegativeInfinity":
        return NegativeInfinity()

    def __repr__(self) -> str:
        return "+inf"


class NegativeInfinity(Singleton):
    """
    The :class:`NegativeInfinity` represents the negative infinity value. It exists
    only one instance of this class called :const:`-INFINITY`.
    """

    __slots__ = ()

    def __lt__(self, other) -> bool:
        return self is not other

    def __le__(self, _) -> bool:
        return True

    def __gt__(self, _) -> bool:
        return False

    def __ge__(self, other) -> bool:
        return self is other

    def __pos__(self) -> "NegativeInfinity":
        return self

    def __neg__(self) -> "PositiveInfinity":
        return INFINITY

    def __repr__(self) -> str:
        return "-inf"


INFINITY = PositiveInfinity()
"""
:const:`INFINITY` represents the infinity value.
"""
