import pygame
from typing import Union, TYPE_CHECKING, Optional

from .base.element import Element
from .base.surfacable import Surfacable

if TYPE_CHECKING:
    pass

from ..size import FIT, SizeType, SequenceSizeType
from ..position import PositionType


class Surface(Surfacable):
    def __init__(
        self,
        surface: Union[pygame.Surface, str, None],
        position: PositionType = None,
        size: SequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
    ):
        self._surface: Optional[pygame.Surface] = None

        self._fit_width: float = 0
        self._fit_height: float = 0

        super().__init__(position, size, width, height, default_size=(FIT, FIT), can_focus=False)
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
        rect = self._draw_rect.move(*offset)
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

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._width.mode == 1:
            if self._surface is not None:
                self._fit_width = (
                    self._surface.get_width() * self._width.percentage
                    + self._width.value
                )
            else:
                self._fit_width = 20

        if self._height.mode == 1:
            if self._surface is not None:
                self._fit_height = (
                    self._surface.get_height() * self._height.percentage
                    + self._height.value
                )
            else:
                self._fit_height = 20

    def _set_surface(self, surface: Union[pygame.Surface, str, None]) -> None:
        self.set_surface(surface)

    def set_surface(
        self, surface: Union[pygame.Surface, str, None], transition=None
    ) -> None:
        if transition:
            transition.old_element = Surface(self._surface)
            self._transition = transition

        if type(surface) is pygame.Surface:
            self._surface = surface
        elif type(surface) is str:
            self._surface = pygame.image.load(surface).convert_alpha()
        else:
            self._surface = None

        self._update_rect_chain_up()

    surface = property(
        fget=lambda self: self._surface,
        fset=_set_surface,
        doc="The pygame.Surface object.",
    )
