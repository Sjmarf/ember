from typing import Optional
from .relative_size import RelativeSize

from ember.axis import Axis, VERTICAL

class Fill(RelativeSize):
    """
    Represents a size relative to the maximum number of pixels available.
    """

    def _get(self, max_value: float) -> float:
        return max_value * self.fraction + self.offset
    
