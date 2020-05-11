# pylint: disable=missing-module-docstring


class Singleton:
    """
    The :class:`Singleton` is used to force a unique instantiation.
    """

    _instance = None

    def __new__(cls, *args) -> "Singleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args)
        return cls._instance

    def __hash__(self) -> int:
        return id(self)
