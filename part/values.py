"""Defines :class:`PositiveInfininy` and :class:`NegativeInfininy` classes."""
# noinspection Mypy
from .utils import Singleton


class PositiveInfinity(Singleton):
    """
    Positive infinity value.

    The :class:`PositiveInfinity` class represents the positive infinity value.
    It exists only one instance of this class called :const:`INFINITY`.
    """

    __slots__ = ()

    def __lt__(self, _) -> bool:
        """Return self<other."""
        return False

    def __le__(self, other) -> bool:
        """Return self<=other."""
        return self is other

    def __gt__(self, other) -> bool:
        """Return self>other."""
        return self is not other

    def __ge__(self, _) -> bool:
        """Return self>=other."""
        return True

    def __pos__(self) -> "PositiveInfinity":
        """Return +self."""
        return self

    def __neg__(self) -> "NegativeInfinity":
        """Return -self."""
        return NegativeInfinity()

    def __repr__(self) -> str:
        """Return repr(self)."""
        return "+inf"


class NegativeInfinity(Singleton):
    """
    Negative infinity value.

    The :class:`NegativeInfinity` class represents the negative infinity value.
    It exists only one instance of this class called :const:`-INFINITY`.
    """

    __slots__ = ()

    def __lt__(self, other) -> bool:
        """Return self<other."""
        return self is not other

    def __le__(self, _) -> bool:
        """Return self<=other."""
        return True

    def __gt__(self, _) -> bool:
        """Return self>other."""
        return False

    def __ge__(self, other) -> bool:
        """Return self>=other."""
        return self is other

    def __pos__(self) -> "NegativeInfinity":
        """Return +self."""
        return self

    def __neg__(self) -> "PositiveInfinity":
        """Return -self."""
        return INFINITY

    def __repr__(self) -> str:
        """Return repr(self)."""
        return "-inf"


INFINITY = PositiveInfinity()
"""
:const:`INFINITY` represents the positive infinity value and
:const:`-INFINITY` represents the negative infinity value.
"""
