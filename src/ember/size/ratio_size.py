from typing import Optional
from .relative_size import RelativeSize

from .. import log

from ember.axis import Axis, VERTICAL


class RatioSize(RelativeSize):
    relies_on_other_value = True

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0, axis: Axis = VERTICAL) -> float:
        return other_value * self.fraction + self.offset
