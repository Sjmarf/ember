import pygame
import importlib.resources
import logging
from typing import Union

from ember import common as _c
from ember.ui.element import Element
from ember.ui.view import View

from ember.style.text_style import TextStyle


class Icon(Element):
    def __init__(self, name, size: Union[tuple[float, float], None] = None,
                 color: Union[str, tuple[int, int, int], pygame.Color, None] = None,
                 style=None):

        # Load the TextStyle object.
        if style is None:
            if _c.default_text_style is None:
                logging.debug("Loading default TextStyle")
                _c.default_text_style = TextStyle()
            self.style = _c.default_text_style
        else:
            self.style = style

        self.col = color if color is not None else self.style.color
        self.set_icon(name)
        super().__init__(*self._surface.get_size() if size is None else size, can_focus=False)

        self.animation = None

    def set_icon(self, name, color: Union[str, tuple[int, int, int], pygame.Color, None] = None, animation=None):
        try:
            if animation:
                old_element = Icon(self._icon, size=(self._width, self._height), color=self.col,
                                   style=self.style)
                old_element.rect = self.rect.copy()
                self._icon = name
                animation = animation.new_element_controller(old_element=old_element, new_element = self)
                self.animation = animation
                
            self._icon = name
            self._surface = pygame.image.load(f'{self.style.font.name}/icons/{name}.png').convert_alpha()
            col = self.col if color is None else color
            
            self._surface.fill(col, special_flags=pygame.BLEND_RGB_ADD)
        except FileNotFoundError:
            raise ValueError(f"'{name}' isn't a valid icon name.")
        self.set_size(*self._surface.get_size())

    def _get_icon(self):
        return self._icon

    def get_surface(self, alpha: int = 255):
        self._surface.set_alpha(alpha)
        return self._surface

    def draw_surface(self, surface: pygame.Surface, offset: tuple[int,int], my_surface: pygame.Surface):
        rect = self.rect.move(*offset)
        surface.blit(my_surface, (rect.x - surface.get_abs_offset()[0], rect.y - surface.get_abs_offset()[1]))

    def _render(self, surface: pygame.Surface, offset: tuple[int, int],
                root: View, alpha: int = 255, _ignore_anim: bool = False):
        self.draw_surface(surface, offset, self.get_surface(alpha))

    icon = property(
        fget=_get_icon,
        fset=set_icon,
        doc="The icon name."
    )
