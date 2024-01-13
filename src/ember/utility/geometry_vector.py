from .. import common as _c
from typing import Optional, Self
import copy

from ember.axis import Axis, HORIZONTAL, VERTICAL


class GeometryVector:
    def __init__(
        self,
        w: float = 0,
        h: float = 0,
        axis: Axis | None = None,
        breadth: float | None = None,
        depth: float | None = None,
    ) -> None:
        self.axis: Axis | None = axis
        self.w: float = w
        self.h: float = h
        if breadth is not None:
            self.breadth = breadth
        if depth is not None:
            self.depth = depth

    def __iter__(self) -> iter:
        return iter((self.w, self.h))

    def __eq__(self, other: "GeometryVector") -> bool:
        if isinstance(other, GeometryVector):
            return other.w == self.w and other.h == self.h
        return False

    def __hash__(self):
        return hash((self.w, self.h))

    def __repr__(self) -> str:
        return f"GeometryVector({self.w}, {self.h}, axis={self.axis})"

    @property
    def depth(self) -> float:
        if self.axis == HORIZONTAL:
            return self.w
        elif self.axis == VERTICAL:
            return self.h
        raise ValueError("No axis")

    @depth.setter
    def depth(self, value: float) -> None:
        if self.axis == HORIZONTAL:
            self.w = value
        elif self.axis == VERTICAL:
            self.h = value
        else:
            raise ValueError("No axis")

    @property
    def breadth(self) -> float:
        if self.axis == HORIZONTAL:
            return self.h
        elif self.axis == VERTICAL:
            return self.w
        raise ValueError("No axis")

    @breadth.setter
    def breadth(self, value: float) -> None:
        if self.axis == HORIZONTAL:
            self.h = value
        elif self.axis == VERTICAL:
            self.w = value
        else:
            raise ValueError("No axis")

    def copy(self) -> Self:
        return copy.copy(self)

    def on_axis(self, axis: Axis) -> Self:
        new = self.copy()
        new.axis = axis
        return new

    ZERO: "GeometryVector"


GeometryVector.ZERO = GeometryVector(0, 0)
