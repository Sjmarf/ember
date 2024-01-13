from typing import Union, Optional, Sequence

import pygame

from .has_geometry import HasGeometry
from ..common import ColorType
from ..position import PositionType, SequencePositionType
from ..size import OptionalSequenceSizeType, SizeType
from ..utility.geometry_vector import GeometryVector


class Surface(HasGeometry):
    def __init__(
        self,
        surface: pygame.Surface | str,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
    ):
        super().__init__(pos=pos, x=x, y=y)
        self._surface: pygame.Surface = None  # noqa
        self.surface = surface

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        surface.blit(self._surface, self.rect)

    def _get_dimensions(
        self,
        proposed_size: GeometryVector,
    ) -> GeometryVector:
        return GeometryVector(*self._surface.get_size())

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @surface.setter
    def surface(self, value: pygame.Surface | str) -> None:
        if isinstance(value, pygame.Surface):
            self._surface = value
        else:
            self._surface = pygame.image.load(value).convert_alpha()
