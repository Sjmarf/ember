from typing import Optional
from .relative_size import RelativeSize

from ember.axis import Axis, VERTICAL

class FillSize(RelativeSize):
    """
    Represents a size relative to the maximum number of pixels available.
    """

    relies_on_max_value = True
  
    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0, axis: Axis = VERTICAL) -> float:
        return max_value * self.fraction + self.offset
    
