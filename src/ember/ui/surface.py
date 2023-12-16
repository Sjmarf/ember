import pygame
from typing import Union, TYPE_CHECKING, Optional, Sequence

from .base.surfacable import Surfacable

if TYPE_CHECKING:
    pass

from ..size import FIT, SizeType, OptionalSequenceSizeType, Fit
from ember.position import PositionType, SequencePositionType


class Surface(Surfacable):
    def __init__(
        self,
        surface: Union[pygame.Surface, str, None],
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        self._surface: Optional[pygame.Surface] = None

        self._min_w: float = 0
        self._min_h: float = 0

        super().__init__(rect, pos, x, y, size, w, h, None, default_size=(FIT, FIT), can_focus=False)
        self.set_surface(surface)

    def __repr__(self) -> str:
        return f"<Surface>"

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255) -> None:
        self._draw_surface(surface, offset, self._get_surface(alpha))

    def _get_surface(self, alpha: int = 255) -> Optional[pygame.Surface]:
        if self._surface is not None:
            self._surface.set_alpha(alpha)
        return self._surface

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self._int_rect.move(*offset)
        if my_surface is not None:
            surface.blit(
                my_surface,
                (
                    rect.x
                    - surface.get_abs_offset()[0]
                    + rect.w / 2
                    - self._surface.get_width() / 2,
                    rect.y
                    - surface.get_abs_offset()[1]
                    + rect.h / 2
                    - self._surface.get_height() / 2,
                ),
            )

    
    def _update_min_size(self) -> None:
        if isinstance(self.w, Fit):
            if self._surface is not None:
                self._min_w = (
                    self._surface.get_width() * self.w.fraction
                    + self.w
                )
            else:
                self._min_w = 20

        if isinstance(self._h, Fit):
            if self._surface is not None:
                self._min_h = (
                    self._surface.get_height() * self._h.fraction
                    + self.h
                )
            else:
                self._min_h = 20
    
    @property
    def surface(self) -> Optional[pygame.Surface]:
       return self._surface
   
    @surface.setter
    def surface(self, surface: Union[pygame.Surface, str, None]) -> None:
        self.set_surface(surface)

    def set_surface(
        self, surface: Union[pygame.Surface, str, None], transition=None
    ) -> None:
        if transition:
            transition.old = Surface(self._surface)
            self._transition = transition

        if type(surface) is pygame.Surface:
            self._surface = surface
        elif type(surface) is str:
            self._surface = pygame.image.load(surface).convert_alpha()
        else:
            self._surface = None

        self.update_min_size()
