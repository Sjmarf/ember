import pygame
import abc
from typing import Optional, Sequence, Union, TYPE_CHECKING

from ember.ui.base.element import Element
from ember.size import SizeType, SequenceSizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
    Position,
    OptionalSequencePositionType,
)

from .has_content_pos import HasContentPos
from ember.state.state import load_background
from ...state.state_controller import StateController
from ember.state.background_state import BackgroundState

from ember.material.material import Material

if TYPE_CHECKING:
    from ember.style.style import Style
    from ...style.container_style import ContainerStyle


class Container(Element, HasContentPos, abc.ABC):
    def __init__(
        self,
        material: Union[BackgroundState, Material, None],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: OptionalSequenceSizeType,
        w: Optional[SizeType],
        h: Optional[SizeType],
        default_size: Optional[Sequence[SizeType]] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        style: Optional["Style"] = None,
    ):
        """
        Base class for Containers. Should not be instantiated directly.
        """

        self._style: ContainerStyle

        Element.__init__(
            self, rect, pos, x, y, size, w, h, style, default_size
        )

        HasContentPos.__init__(self, content_pos, content_x, content_y)

        self.state_controller: StateController = StateController(self)
        self._state: Optional[BackgroundState] = load_background(self, material)

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

    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        pass

    @property
    def material(self) -> "Material":
        return self._state.material

    @material.setter
    def material(self, new_material: Union[BackgroundState, Material, None]) -> None:
        self._state = load_background(self, new_material)
