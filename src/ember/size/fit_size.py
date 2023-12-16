from typing import Optional
from .relative_size import RelativeSize

from ember.axis import Axis, VERTICAL

class Fit(RelativeSize):
    """
    Represents a size relative to the minimum number of pixels available.
    """
    
    def _get(self, min_value: float) -> float:
        return min_value * self._fraction + self._offset
