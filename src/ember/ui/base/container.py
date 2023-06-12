import pygame
import abc
from typing import Optional, Sequence, Union, TYPE_CHECKING

from ember import common as _c
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType, SequenceSizeType
from ember.position import PositionType, SequencePositionType

from ember.state.state import load_background
from ember.state.background_state import BackgroundState

from ember.material.material import Material

if TYPE_CHECKING:
    from ember.style.container_style import ContainerStyle


class Container(Element, abc.ABC):
    def __init__(
        self,
        material: Union[BackgroundState, Material, None],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: Optional[SequenceSizeType],
        width: Optional[SizeType],
        height: Optional[SizeType],
        default_size: Sequence[SizeType],
    ):
        """
        Base class for Containers. Should not be instantiated directly.
        """
        self._state: Optional[BackgroundState] = load_background(self, material)

        super().__init__(rect, pos, x, y, size, width, height, default_size=default_size)

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
        rect = self._int_rect.move(*offset)
        self.state_controller.set_state(
            self._style.state_func(self), transitions=(self._style.material_transition,)
        )
        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0],
                rect.y - surface.get_abs_offset()[1],
            ),
            rect.size,
            alpha,
        )

    @abc.abstractmethod
    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        pass

    def _set_style(self, style: "ContainerStyle") -> None:
        self.set_style(style)

    def set_style(self, style: "ContainerStyle") -> None:
        """
        Set the style of the Container.
        """
        self._style: "ContainerStyle" = self._get_style(style)

    style: "ContainerStyle" = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ContainerStyle of the Container. Synonymous with the set_style() method.",
    )

    @property
    def material(self) -> "Material":
        return self._state.material

    @material.setter
    def material(self, new_material: Union[BackgroundState, Material, None]) -> None:
        self._state = load_background(self, new_material)
