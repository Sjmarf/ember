from .position import Position

from ember.axis import Axis, VERTICAL


class InterpolatedPosition(Position):
    """
    Used by animations to interpolate between two other Position objects.
    """

    def __init__(self, old_pos: Position, new_pos: Position) -> None:
        self.old_pos: Position = old_pos
        self.new_pos: Position = new_pos
        self.progress: float = 0

    def __repr__(self):
        return f"<InterpolatedPosition({self.old_pos} -> {self.new_pos}: {self.progress*100: .0f}%)>"

    def get(self, container_size: float = 0, element_size: float = 0, axis: Axis = VERTICAL) -> float:
        old_val = self.old_pos.get(container_size, element_size, axis)
        new_val = self.new_pos.get(container_size, element_size, axis)
        return old_val + (new_val - old_val) * self.progress
