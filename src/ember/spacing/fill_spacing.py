from typing import Optional
import pygame
import math
from .spacing import Spacing


class FillSpacing(Spacing):
    def __init__(self, min_value: int = 0, max_value: Optional[int] = None) -> None:
        self.min_value: int = min_value
        self.max_value: int = max_value if max_value is not None else math.inf

    def get(self, available_size: int = 0) -> float:
        return pygame.math.clamp(self.min_value, available_size, self.max_value)

    def get_min(self) -> int:
        return self.min_value
