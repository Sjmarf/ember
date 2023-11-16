from abc import ABC, abstractmethod
from typing import Union, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ember.trait import Trait
    from ember.ui.element import Element
    from ember.ui.can_pivot import CanPivot

from ember.axis import Axis, HORIZONTAL, VERTICAL

class Position(ABC):
    @abstractmethod
    def get(self, container_size: float = 0, element_size: float = 0, axis: Axis = VERTICAL) -> float:
        ...
        
    def __or__(self, other: Union["Position", int]) -> "PivotablePosition":
        return PivotablePosition(self, other)
    
    def __ror__(self, other: Union["Position", int]) -> "PivotablePosition":
        return PivotablePosition(other, other)
    
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

    def get(self, container_size: float = 0, element_size: float = 0, axis: Axis = VERTICAL) -> float:
        return self.value
    

class PivotablePosition(Position):
    def __init__(self, horizontal_pos: Position | int, vertical_pos: Position | int, watching: Optional["CanPivot"] = None) -> None:
        self.horizontal_pos: Position = load_position(horizontal_pos)
        self.vertical_pos: Position = load_position(vertical_pos)
        self.watching: Optional["CanPivot"] = watching
        
    def get(self, container_size: float = 0, element_size: float = 0, axis: Axis = VERTICAL) -> float:
        if self.watching is not None:
            axis = self.watching.axis
        if axis == HORIZONTAL:
            return self.horizontal_pos.get(container_size, element_size, axis)
        return self.vertical_pos.get(container_size, element_size, axis)

    def __invert__(self) -> "PivotablePosition":
        return PivotablePosition(self.vertical_pos, self.horizontal_pos, self.watching)


def load_position(pos: Union["Position", float, "Trait", None]) -> Union["Position", "Trait", None]:
    return AbsolutePosition(pos) if isinstance(pos, (int, float)) else pos