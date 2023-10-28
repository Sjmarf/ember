from typing import Optional
import math
import pygame
from .resizable_size import ResizableSize
from .size import Size, SizeType, load_size
from .. import common as _c

from ember.axis import Axis, VERTICAL


class ClampedSize(ResizableSize):
    relies_on_min_value = True
    relies_on_max_value = True
    relies_on_other_value = True

    def __init__(
        self,
        size: SizeType,
        min_size: Optional[SizeType] = None,
        max_size: Optional[SizeType] = None,
    ) -> None:
        self._size: Size = load_size(size)
        self._size._parent_dependencies.add(self)

        self._min_size: Optional[Size] = load_size(min_size)
        if self._min_size is not None:
            self._min_size._parent_dependencies.add(self)

        self._max_size: Optional[Size] = load_size(max_size)
        if self._max_size is not None:
            self._max_size._parent_dependencies.add(self)

        super().__init__()

    def __repr__(self) -> str:
        return f"<ClampedSize(size={self._size}, min_size={self._min_size}, max_size={self._max_size})>"

    def __add__(self, other: int) -> "ClampedSize":
        return ClampedSize(
            size=self._size + other, min_size=self._min_size, max_size=self._max_size
        )

    def __sub__(self, other: int) -> "ClampedSize":
        return ClampedSize(
            size=self._size - other, min_size=self._min_size, max_size=self._max_size
        )

    def _set_value(self, value: int) -> None:
        if isinstance(self.size, ResizableSize):
            self._size._set_value(value)
        else:
            raise _c.Error(
                "Size value contained within ClampedSize doesn't support Resizable."
            )

    def update_pair_value(self, value: float) -> bool:
        return (
            self._min_size.update_pair_value(value)
            or self._size.update_pair_value(value)
            or self._max_size.update_pair_value(value)
        )

    def get(
        self,
        min_value: float = 0,
        max_value: Optional[float] = None,
        other_value: float = 0,
        axis: Axis = VERTICAL,
    ) -> float:
        min_size = (
            self._min_size.get(min_value, max_value, other_value)
            if self._min_size is not None
            else -math.inf
        )
        max_size = (
            self._max_size.get(min_value, max_value, other_value)
            if self._max_size is not None
            else math.inf
        )

        size = self._size.get(min_value, max_value, other_value)
        return pygame.math.clamp(size, min_size, max_size)

    def copy(self) -> "ClampedSize":
        return ClampedSize(
            self._size.copy(), self._min_size.copy(), self._max_size.copy()
        )

    @property
    def size(self) -> Size:
        return self._size

    @size.setter
    @Size.triggers_trait_update
    def size(self, size: SizeType) -> None:
        if (new_size := load_size(size)) is not self._size:
            if self in self._size.parent_sizes:
                self._size.parent_sizes.remove(self)
            self._size = new_size
            new_size.parent_sizes.add(self)

    @property
    def min_size(self) -> Optional[Size]:
        return self._min_size

    @min_size.setter
    @Size.triggers_trait_update
    def min_size(self, size: Optional[SizeType]) -> None:
        if (new_size := load_size(size)) is not self._min_size:
            if self._min_size is not None and self in self._min_size.parent_sizes:
                self._min_size.parent_sizes.remove(self)
            self._min_size = new_size
            if new_size is not None:
                new_size.parent_sizes.add(self)

    @property
    def max_size(self) -> Optional[Size]:
        return self._max_size

    @max_size.setter
    @Size.triggers_trait_update
    def max_size(self, size: Optional[SizeType]) -> None:
        if (new_size := load_size(size)) is not self._max_size:
            if self._max_size is not None and self in self._max_size.parent_sizes:
                self._max_size.parent_sizes.remove(self)
            self._max_size = new_size
            if new_size is not None:
                new_size.parent_sizes.add(self)
