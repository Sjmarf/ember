from typing import Optional
import math
import pygame
from .resizable_size import ResizableSize
from .size import Size, SizeType
from .load_size import load_size
from .. import common as _c


class ClampedSize(ResizableSize):
    relies_on_min_value = True

    def __init__(
        self,
        size: SizeType,
        min_size: Optional[SizeType] = None,
        max_size: Optional[SizeType] = None,
    ) -> None:
        self.size: Size = load_size(size)
        self.min_size: Optional[Size] = load_size(min_size)
        self.max_size: Optional[Size] = load_size(max_size)

    def _set_value(self, value: int) -> None:
        if isinstance(self.size, ResizableSize):
            self.size._set_value(value)
        else:
            raise _c.Error(
                "Size value contained within ClampedSize doesn't support Resizable."
            )

    def update_pair_value(self, value: float) -> bool:
        return (
            self.min_size.update_pair_value(value)
            or self.size.update_pair_value(value)
            or self.max_size.update_pair_value(value)
        )

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        min_size = (
            self.min_size.get(min_value, max_value) if self.min_size is not None else 0
        )
        max_size = (
            self.max_size.get(min_value, max_value)
            if self.max_size is not None
            else math.inf
        )

        size = self.size.get(min_value, max_value)
        return pygame.math.clamp(size, min_size, max_size)
