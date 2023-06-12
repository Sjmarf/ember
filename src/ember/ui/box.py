import pygame
from typing import Union, Optional, Literal, TYPE_CHECKING, Sequence

from .base.single_element_container import SingleElementContainer
from .base.element import Element
from .view import ViewLayer
from ..material.material import Material
from ..state.state_controller import StateController

from ..size import FIT, FILL, SizeType, SequenceSizeType, SizeMode
from ..position import PositionType, CENTER, SequencePositionType

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle
    from ..state.background_state import BackgroundState

from .. import common as _c
from .. import log


class Box(SingleElementContainer):
    """
    A Box is a container that can optionally hold one Element.
    """

    def __init__(
        self,
        element: Optional[Element],
        material: Union["BackgroundState", Material, None] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        self.set_style(style)

        self._fit_width: float = 0
        self._fit_height: float = 0

        self.layer = None

        self._element: Optional[Element] = None

        self.set_element(element, _update=False)

        super().__init__(material, rect, pos, x, y, size, width, height)

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object is responsible for managing the Box's 
        background states.
        """

        self._update_rect_chain_up()

    def __repr__(self) -> str:
        return "<Box>"

    def _update(self) -> None:
        if self._element and self._element.is_visible:
            self._element._update_a()

    def _update_rect_chain_down(
        self,
        surface: pygame.Surface,
        pos: tuple[float, float],
        max_size: tuple[float, float],
        _ignore_fill_width: bool = False,
        _ignore_fill_height: bool = False,
    ) -> None:
        super()._update_rect_chain_down(
            surface, pos, max_size, _ignore_fill_width, _ignore_fill_height
        )

        if self._element:
            element_x = (
                pos[0]
                + self.get_ideal_width(max_size[0]) // 2
                - self._element.get_ideal_width(self.rect.w) // 2
            )
            element_y = (
                pos[1]
                + self.get_ideal_height(max_size[1]) // 2
                - self._element.get_ideal_height(self.rect.h) // 2
            )
            element_w = self._element.get_ideal_width(self.rect.w)
            element_h = self._element.get_ideal_height(self.rect.h)

            if not self.is_visible:
                self._element.is_visible = False
            elif (
                element_x + element_w < surface.get_abs_offset()[0]
                or element_x > surface.get_abs_offset()[0] + surface.get_width()
                or element_y + element_h < surface.get_abs_offset()[1]
                or element_y > surface.get_abs_offset()[1] + surface.get_height()
            ):
                self._element.is_visible = False
            else:
                self._element.is_visible = True

            self._element._update_rect_chain_down(
                surface,
                (element_x, element_y),
                self.rect.size,
            )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._h.mode == SizeMode.FIT:
            if self._element:
                self._fit_height = self._element.get_ideal_height()
            else:
                self._fit_height = 20

        if self._w.mode == SizeMode.FIT:
            if self._element:
                self._fit_width = self._element.get_ideal_width()
            else:
                self._fit_width = 20

    def _set_layer_chain(self, layer: ViewLayer) -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer: Optional[ViewLayer] = layer
        if self._element is not None:
            self._element._set_layer_chain(layer)

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if direction == _c.FocusDirection.OUT:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)
        elif (
            direction
            in {
                _c.FocusDirection.LEFT,
                _c.FocusDirection.RIGHT,
                _c.FocusDirection.UP,
                _c.FocusDirection.DOWN,
                _c.FocusDirection.FORWARD,
            }
            or self._element is None
        ):
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(self, f"-> child {self._element}.")
            return self._element._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        if self._element is not None:
            return self._element._event(event)
        return False
