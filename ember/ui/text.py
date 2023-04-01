import pygame
import logging
from typing import Union, Optional, Literal, TYPE_CHECKING
from copy import deepcopy

import ember
from ember import common as _c
from ember.ui.element import Element
from ember.style.text_style import TextStyle
from ember.transition.transition import Transition

from ember.font.ttf_font import Line

if TYPE_CHECKING:
    from ember.ui.view import View

from ember.size import FIT


class Text(Element):
    def __init__(self,
                 text,
                 size: Union[tuple[float, float], None] = None,
                 width: Union[float, None] = None,
                 height: Union[float, None] = None,
                 variant: Optional[str] = None,
                 align: Literal["left","center","right"] = "center",
                 color: Union[str, tuple[int, int, int], pygame.Color, None] = None,
                 style: Union[TextStyle, None] = None):

        # Load the TextStyle object.
        if style is None:
            if _c.default_text_style is None:
                logging.debug("Loading default TextStyle")
                _c.default_text_style = TextStyle()
            self.style = _c.default_text_style
        else:
            self.style = style

        # Determine which colour to use.
        if color:
            self._col = color
        else:
            self._col = self.style.color

        self._variant = self.style.variant if variant is None else variant
        self._text = text

        self.align = align

        self._fit_width = 0
        self._fit_height = 0

        if size is None:
            size = (0, 0)
            if width is None:
                width = FIT
            if height is None:
                height = FIT

        if width is not None:
            size = (width, size[1])
        if height is not None:
            size = (size[0], height)

        super().__init__(*size, selectable=False)
        self.surface = None

        self.lines = []

        self._update_surface()

    def __repr__(self):
        return f"'{self._text}'"

    def set_text(self, text: str, color: Union[tuple[int, int, int], str, pygame.Color, None] = None,
                 animation: Optional[Transition] = None):
        if text != self._text:
            if animation:
                # It's necessary to create temporary variables here, so that the width and height are accurate
                old_element = Text(self._text, size=(self.width, self.height), color=self._col,
                                   style=self.style)
                old_element.rect = self.rect.copy()
                animation = animation.new_element_controller(old_element=old_element, new_element=self)
                self.animation = animation

            self._text = text
            self._col = color if color is not None else self._col
            self._update_surface()

    def _get_text(self):
        return self._text

    def get_line(self, line_index) -> Line:
        try:
            return self.lines[line_index]
        except IndexError:
            return None

    def get_line_index_from_letter_index(self, letter_index):
        n = 0
        for n, i in enumerate(self.lines):
            if letter_index < i.start_index:
                return n - 1
        return n

    def set_color(self, color: Union[str, tuple[int, int, int], pygame.Color, None] = None, animation=None):
        if animation:
            old_element = Text(self._text, size=(self.width, self.height), color=self._col,
                               style=self.style)
            old_element.rect = self.rect.copy()
            animation = animation.new_element_controller(old_element=old_element, new_element=self)
            self.animation = animation

        self._col = color
        self._update_surface()

    def _get_color(self):
        return self._col

    def calc_fit_size(self):
        if self.width.mode == 1:
            self._fit_width = self.surface.get_width()
        if self.height.mode == 1:
            self._fit_height = self.surface.get_height()

        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()

    def set_width(self, value):
        super().set_width(value)
        self._update_surface()

    def check_for_surface_update(self):
        # This is in a separate method because VScroll needs to call this before its scroll calculations
        if self.surface is None or (self.width.mode == 2 and self.rect.w != self.surface.get_width()):
            self._update_surface()
            return True

    def _update_surface(self):
        max_width = None if self.width.mode == 1 else self.rect.w
        if self.rect.w == 0 and max_width is not None:
            return
        self.surface, self.lines = \
            self.style.font.render(self._text, col=self._col, variant=self._variant,
                                   outline_col=self.style.outline_color,
                                   max_width=max_width, align=self.align if self.align else self.style.align)
        self.calc_fit_size()

    def get_surface(self, alpha: int = 255):
        self.check_for_surface_update()
        self.surface.set_alpha(alpha)
        return self.surface

    def draw_surface(self, surface: pygame.Surface, offset: tuple[int, int], my_surface: pygame.Surface):
        rect = self.rect.move(*offset)
        pos = (rect.centerx - my_surface.get_width() // 2,
               rect.centery - my_surface.get_height() // 2)
        surface.blit(my_surface, (pos[0] - surface.get_abs_offset()[0], pos[1] - surface.get_abs_offset()[1] +
                                  self.style.font.y_offset))

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View",
               alpha: int = 255):
        self.draw_surface(surface, offset, self.get_surface(alpha))

    text = property(
        fget=_get_text,
        doc="The text string."
    )

    color = property(
        fget=_get_color,
        doc="The color of the text."
    )
