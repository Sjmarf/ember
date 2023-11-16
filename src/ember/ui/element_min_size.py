from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember.axis import Axis, HORIZONTAL


class ElementMinSize:
    def __init__(self) -> None:
        self.w: float = 0
        self.h: float = 0

    def __getitem__(self, item: int) -> float:
        if isinstance(item, int):
            if item == 0:
                return self.w
            return self.h

        return NotImplemented

    def __setitem__(self, key: int, value: float):
        if key == 0:
            self.w = value
        else:
            self.h = value
