import pygame
from typing import Union, Optional

from .. import common as _c
from ..common import ColorType
from .base.element import Element
from .base.surfacable import Surfacable

from ..style.text_style import TextStyle
from ..size import FIT, SizeType, SequenceSizeType
from ..position import PositionType
from ..style.load_style import load as load_style

from ..transition.transition import Transition
from ..style.get_style import _get_style


class Icon(Surfacable):
    def __init__(
        self,
        name: Union[str, pygame.Surface],
        color: Optional[ColorType] = None,
        position: PositionType = None,
        size: SequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
        style: TextStyle = None,
    ):
        self._name: Optional[str] = None

        self._fit_width: float = 0
        self._fit_height: float = 0

        self.set_style(style)

        self._color = color if color is not None else self._style.color
        super().__init__(position, size, width, height, (FIT, FIT), can_focus=False)
        self.set_icon(name)

    def __repr__(self) -> str:
        return f"<Icon({self._name})>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        self._draw_surface(surface, offset, self._get_surface(alpha))

    def _get_surface(self, alpha: int = 255) -> pygame.Surface:
        self._surface.set_alpha(alpha)
        return self._surface

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self._draw_rect.move(*offset)
        surface.blit(
            my_surface,
            (
                rect.centerx
                - my_surface.get_width() // 2
                - surface.get_abs_offset()[0],
                rect.centery
                - my_surface.get_height() // 2
                - surface.get_abs_offset()[1],
            ),
        )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._surface:
            if self._width.mode == 1:
                self._fit_width = self._surface.get_width()
            if self._height.mode == 1:
                self._fit_height = self._surface.get_height()

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

            self._surface.fill(col, special_flags=pygame.BLEND_RGB_ADD)
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
        self._surface.fill(self._color, special_flags=pygame.BLEND_RGB_ADD)
        self._update_rect_chain_up()

    def _set_style(self, style: Optional[TextStyle]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional[TextStyle]) -> None:
        """
        Sets the TextStyle of the Icon.
        """
        self._style: TextStyle = _get_style(style, "text")

    name: str = property(
        fget=lambda self: self._name, fset=_set_icon, doc="The Icon name."
    )

    surface = property(
        fget=lambda self: self._surface, fset=_set_icon, doc="The Icon surface."
    )

    color = property(fget=lambda self: self._color, doc="The color of the Icon.")

    style: TextStyle = property(
        fget=lambda self: self._style, fset=_set_style, doc="The TextStyle of the Icon."
    )
