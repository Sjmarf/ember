from .spacing import Spacing


class AbsoluteSpacing(Spacing):
    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other):
        if isinstance(other, AbsoluteSpacing):
            return self.value == other.value
        return False

    def __add__(self, other: int):
        return AbsoluteSpacing(self.value + other)

    def __sub__(self, other: int):
        return AbsoluteSpacing(self.value + other)

    def get(self, available_size: int = 0) -> int:
        return self.value

    def get_min(self) -> int:
        return self.value
