from .position import Position


class AnchorPosition(Position):
    __slots__ = ("value", "percent", "size_offset")

    def __init__(self, value: int, percent: float = 0, padding: float = 0) -> None:
        self.value: int = value
        self.percent: float = percent
        self.padding: float = padding

    def __repr__(self):
        return f"<Position({self.percent*100}% + {self.value})>"

    def __eq__(self, other) -> bool:
        if isinstance(other, AnchorPosition):
            return (
                self.value == other.value
                and self.percent == other.percent
            )
        return False

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value + other, self.percent)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value - other, self.percent)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value, self.percent * other)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value, self.percent / other)
        else:
            return NotImplemented

    def get(self, container_size: float = 0, element_size: float = 0) -> float:
        return (
            self.padding
            + element_size / 2
            + (
                ((container_size - self.padding * 2 - element_size) * self.percent)
                - element_size * 0.5
                + self.value
            )
        )


class LeftPosition(AnchorPosition):
    pass


class RightPosition(AnchorPosition):
    pass


class TopPosition(AnchorPosition):
    pass


class BottomPosition(AnchorPosition):
    pass


class CenterPosition(AnchorPosition):
    pass
