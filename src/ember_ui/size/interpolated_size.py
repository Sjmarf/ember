from typing import Optional
from .size import Size

from ember_ui.axis import Axis, VERTICAL


class InterpolatedSize(Size):
    """
    Used by animations to interpolate between two other Size objects.
    """

    def _relies_on_min_value(self) -> bool:
        return self.old_size.relies_on_min_value or self.new_size.relies_on_min_value

    relies_on_min_value = property(fget=_relies_on_min_value)

    def __init__(self, old_size: "Size", new_size: "Size", progress: float = 0) -> None:
        self.old_size: "Size" = old_size
        self.new_size: "Size" = new_size
        self.progress: float = progress
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, InterpolatedSize):
            return (
                self.progress == other.progress
                and self.old_size == other.old_size
                and self.new_size == other.new_size
            )
        return False

    def __repr__(self) -> str:
        return f"<InterpolatedSize({self.old_size} -> {self.new_size}: {self.progress*100: .0f}%)>"

    def update_pair_value(self, value: float) -> bool:
        return self.new_size.update_pair_value(
            value
        ) or self.old_size.update_pair_value(value)

    def get(
        self,
        min_value: float = 0,
        max_value: Optional[float] = None,
        other_value: float = 0,
        axis: Axis = VERTICAL,
    ) -> float:
        old_val = self.old_size.get(min_value, max_value, other_value)
        new_val = self.new_size.get(min_value, max_value, other_value)
        return round(old_val + (new_val - old_val) * self.progress)

    def copy(self) -> "InterpolatedSize":
        return InterpolatedSize(self.old_size, self.new_size, progress=self.progress)
