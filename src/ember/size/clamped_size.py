from typing import Optional
import math
import pygame
from .size import Size, SizeType, load_size
from .. import common as _c

from ember.axis import Axis, VERTICAL

from ember.trait.dependency_child import DependencyChild


class Clamped(Size):

    size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)
    min_size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)
    max_size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)
    
    def __init__(
        self,
        size: SizeType,
        min_size: Optional[SizeType] = None,
        max_size: Optional[SizeType] = None,
    ) -> None:
        
        super().__init__()
                
        self.size = size
        self.min_size = min_size
        self.max_size = max_size

        self.calculate_instance_intents()

    def __repr__(self) -> str:
        return f"<ClampedSize(size={self._size}, min_size={self._min_size}, max_size={self._max_size})>"

    def __add__(self, other: int) -> "Clamped":
        return Clamped(
            size=self._size + other, min_size=self._min_size, max_size=self._max_size
        )

    def __sub__(self, other: int) -> "Clamped":
        return Clamped(
            size=self._size - other, min_size=self._min_size, max_size=self._max_size
        )
    
    def __iter__(self):
        return iter((self._min_size, self._size, self._max_size))

    def update_pair_value(self, value: float) -> bool:
        return (
            self._min_size.update_pair_value(value)
            or self._size.update_pair_value(value)
            or self._max_size.update_pair_value(value)
        )

    def _get(self, *args, **kwargs) -> float:
        min_size = (
            self._min_size.get(*args, **kwargs)
            if self._min_size is not None
            else -math.inf
        )
        max_size = (
            self._max_size.get(*args, **kwargs)
            if self._max_size is not None
            else math.inf
        )

        size = self._size.get(*args, **kwargs)
        return pygame.math.clamp(size, min_size, max_size)

    def copy(self) -> "Clamped":
        return Clamped(
            self._size.copy(), self._min_size.copy(), self._max_size.copy()
        )
