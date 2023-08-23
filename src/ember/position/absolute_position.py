from .position import Position

class AbsolutePosition(Position):
    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self):
        return f"<AbsolutePosition({self.value}px)>"

    def __eq__(self, other):
        if isinstance(other, AbsolutePosition):
            return self.value == other.value
        return False

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value + other)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value - other)
        else:
            return NotImplemented

    def get(self, container_size: float = 0, element_size: float = 0) -> float:
        return self.value
