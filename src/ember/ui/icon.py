import pygame
import inspect
from typing import Union, Optional, TYPE_CHECKING, Sequence

from .. import common as _c
from ..common import ColorType
from .base.element import Element
from .base.surfacable import Surfacable

from ..size import FIT, SizeType, SequenceSizeType, SizeMode
from ..position import PositionType, CENTER, SequencePositionType
from .text import Text

if TYPE_CHECKING:
    from ..style.text_style import TextStyle

from ..transition.transition import Transition


class Icon(Surfacable):
    def __init__(
        self,
        name: Union[str, pygame.Surface],
        color: Optional[ColorType] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: "TextStyle" = None,
    ):
        self._name: Optional[str] = None

        self._min_w: float = 0
        self._min_h: float = 0

        self.set_style(style)

        self._color = color
        super().__init__(rect, pos, x, y, size, width, height, (FIT, FIT), can_focus=False)
        self.set_icon(name)

    def __repr__(self) -> str:
        return f"<Icon({self._name})>"

    def _get_surface(self, alpha: int = 255) -> pygame.Surface:
        self._surface.set_alpha(alpha)
        return self._surface

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self._int_rect.move(*offset)

        pos = (
                rect.centerx
                - my_surface.get_width() // 2
                - surface.get_abs_offset()[0],
                rect.centery
                - my_surface.get_height() // 2
                - surface.get_abs_offset()[1],
            )

        if self._color is None:
            new_surface = my_surface.copy()
            self._style.material.render(self, surface, pos, new_surface.get_size(), alpha=255)
            new_surface.blit(self._style.material.get(self), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        else:
            new_surface = my_surface

        surface.blit(
            new_surface,
            pos
        )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._surface:
            self._min_w = self._surface.get_width()
            self._min_h = self._surface.get_height()

    def _set_icon(self, name: str) -> None:
        self.set_icon(name)

    def set_icon(
        self,
        name: Union[str, pygame.Surface],
        color: Optional[ColorType] = None,
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Set the icon image.
        """
        try:
            if transition:
                old_element = self.copy()
                transition = transition._new_element_controller(
                    old_element=old_element, new_element=self
                )
                self._transition = transition

            if isinstance(name, str):
                self._name = name
                path = (
                    name if "." in name else f"{self.style.font.name}/icons/{name}.png"
                )
                self._surface = pygame.image.load(path).convert_alpha()

            elif isinstance(name, pygame.Surface):
                self._name = None
                self._surface = name

            col = self._color if color is None else color

            self._surface.fill(col if col is not None else (0,0,0), special_flags=pygame.BLEND_RGB_ADD)
        except FileNotFoundError:
            raise ValueError(f"'{name}' isn't a valid icon name.")
        self._update_rect_chain_up()

    def set_color(
        self,
        color: Optional[ColorType] = None,
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Set the color of the Icon.
        """
        if transition:
            old_element = self.copy()
            old_element._surface = self._surface.copy()
            transition = transition._new_element_controller(
                old_element=old_element, new_element=self
            )
            self._transition = transition

        self._color = color

        self._surface.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_SUB)
        if color is not None:
            self._surface.fill(self._color, special_flags=pygame.BLEND_RGB_ADD)
        self._update_rect_chain_up()

    def _set_style(self, style: Optional["TextStyle"]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional["TextStyle"]) -> None:
        """
        Sets the TextStyle of the Icon.
        """
        self._style: "TextStyle" = self._get_style(style, type(self), Text, *inspect.getmro(type(self)))

    name: str = property(
        fget=lambda self: self._name, fset=_set_icon, doc="The Icon name."
    )

    surface = property(
        fget=lambda self: self._surface, fset=_set_icon, doc="The Icon surface."
    )

    color = property(fget=lambda self: self._color, doc="The color of the Icon.")

    style: "TextStyle" = property(
        fget=lambda self: self._style, fset=_set_style, doc="The TextStyle of the Icon."
    )
