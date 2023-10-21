from typing import Optional
from .relative_size import RelativeSize

from ember.axis import Axis, VERTICAL

class FitSize(RelativeSize):
    """
    Represents a size relative to the minimum number of pixels available.
    """

    relies_on_min_value = True

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0, axis: Axis = VERTICAL) -> float:
        return min_value * self._fraction + self._offset
