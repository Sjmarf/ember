import pygame
import abc
from typing import Optional, Sequence, Union

from ember import common as _c
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType
from ember.position import PositionType

from ember.style.container_style import ContainerStyle
from ember.style.load_style import load as load_style
from ...style.get_style import _get_style


class Container(Element, abc.ABC):
    def __init__(
        self,
        position: PositionType,
        size: Sequence[SizeType],
        width: SizeType,
        height: SizeType,
        default_size: Sequence[SizeType] = (20, 20),
    ):
        """
        Base class for Containers. Should not be instantiated directly.
        """
        super().__init__(position, size, width, height, default_size=default_size)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        self._render_background(surface, offset, alpha)
        self._render_elements(surface, offset, alpha)

    def _render_background(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        rect = self._draw_rect.move(*offset)
        self.state_controller.render(
            self._style.state_func(self),
            surface,
            (
                rect.x - surface.get_abs_offset()[0],
                rect.y - surface.get_abs_offset()[1],
            ),
            rect.size,
            alpha,
            transition=self._style.material_transition
        )

    @abc.abstractmethod
    def _render_elements(
            self,
            surface: pygame.Surface,
            offset: tuple[int, int],
            alpha: int = 255,
    ) -> None:
        pass

    def _set_style(self, style: ContainerStyle) -> None:
        self.set_style(style)

    def set_style(self, style: ContainerStyle) -> None:
        """
        Set the style of the Container.
        """
        self._style: ContainerStyle = _get_style(style, "container")

    style = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ContainerStyle of the Container. Synonymous with the set_style() method.",
    )
