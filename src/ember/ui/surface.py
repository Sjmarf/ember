import pygame
from typing import Union, TYPE_CHECKING

from .element import Element

if TYPE_CHECKING:
    from .view import View

from ..size import FIT


class Surface(Element):
    def __init__(self, surface: Union[pygame.Surface, str, None], size: Union[tuple[float, float], None] = None):
        if size is None:
            size = (FIT, FIT)
        self._fit_width = 0
        self._fit_height = 0

        super().__init__(*size, can_focus=False)
        self.animation = None
        self.set_surface(surface)

    def __repr__(self):
        return f"<Surface>"

    def _update_rect_chain_up(self):
        if self._width.mode == 1:
            if self.surface is not None:
                self._fit_width = self.surface.get_width() * self._width.percentage + self._width.value
            else:
                self._fit_width = 20

        if self._height.mode == 1:
            if self.surface is not None:
                self._fit_height = self.surface.get_height() * self._height.percentage + self._height.value
            else:
                self._fit_height = 20

    def set_surface(self, surface: Union[pygame.Surface, str, None], animation=None):
        if animation:
            animation.old_element = Surface(self.surface)
            self.animation = animation

        if type(surface) is pygame.Surface:
            self.surface = surface
        elif type(surface) is str:
            self.surface = pygame.image.load(surface).convert_alpha()
        else:
            self.surface = None

        self._update_rect_chain_up()

    def get_surface(self, alpha: int = 255):
        if self.surface is not None:
            self.surface.set_alpha(alpha)
        return self.surface

    def draw_surface(self, surface: pygame.Surface, offset: tuple[int,int], my_surface: pygame.Surface):
        rect = self.rect.move(*offset)
        if my_surface is not None:
            surface.blit(my_surface, (rect.x - surface.get_abs_offset()[0] +
                                      rect.w / 2 - self.surface.get_width() / 2,
                                      rect.y - surface.get_abs_offset()[1] +
                                      rect.h / 2 - self.surface.get_height() / 2
                                      ))

    def _render(self, surface: pygame.Surface, offset: tuple[int, int],
                root: "View", alpha: int = 255):
        self.draw_surface(surface, offset, self.get_surface(alpha))
