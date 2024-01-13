from .. import common as _c
from typing import Optional, Self
from ember.utility.geometry_vector import GeometryVector
import copy
import itertools

from ember.axis import Axis, HORIZONTAL, VERTICAL

class GeometryRect:
    def __init__(self, origin: GeometryVector, size: GeometryVector) -> None:
        self.origin: GeometryVector = origin
        self.size: GeometryVector = size
        
    def __iter__(self) -> iter:
        return itertools.chain(self.origin, self.size)
    
    def __eq__(self, other: "GeometryRect") -> bool:
        if isinstance(other, GeometryRect):
            return other.origin == self.origin and other.size == self.size
        return False
    
    def copy(self) -> Self:
        return type(self)(copy.copy(self.origin), copy.copy(self.size))
    