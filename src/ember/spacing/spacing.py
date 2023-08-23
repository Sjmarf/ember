import pygame
import math
from typing import Union, Sequence, Optional
from abc import ABC, abstractmethod


class Spacing(ABC):
    @abstractmethod
    def get(self, available_size: int = 0) -> int:
        pass

    @abstractmethod
    def get_min(self) -> int:
        pass


SpacingType = Union[Spacing, int]
