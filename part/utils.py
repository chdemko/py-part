"""Utility module that defines the :class:`Singleton` class."""


class Singleton:
    """
    Singleton class.

    The :class:`Singleton` class is used to force a unique instantiation.
    """

    _instance = None

    def __new__(cls, *args) -> "Singleton":
        """Control single instance creation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args)
        return cls._instance

    def __hash__(self) -> int:
        """Return hash(self)."""
        return id(self)
