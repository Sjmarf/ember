from typing import Optional
from .relative_size import RelativeSize

from .. import log

from ember.axis import Axis, VERTICAL


class Ratio(RelativeSize):    
    def _get(self, other_value: float) -> float:
        return other_value * self.fraction + self.offset
