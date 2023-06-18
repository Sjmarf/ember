import pygame
from typing import Union, Optional, Literal, TYPE_CHECKING, Sequence

from .base.single_element_container import SingleElementContainer
from .base.element import Element
from .view import ViewLayer
from ..material.material import Material
from ..state.state_controller import StateController

from ..size import (
    FIT,
    FILL,
    SizeType,
    SequenceSizeType,
    SizeMode,
    OptionalSequenceSizeType,
)
from ..position import PositionType, CENTER, SequencePositionType, OptionalSequencePositionType

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle
    from ..state.background_state import BackgroundState

from .. import common as _c
from ..common import INHERIT, InheritType
from .. import log


class Box(SingleElementContainer):
    """
    A Box is a container that can optionally hold one Element.
    """

    def __init__(
        self,
        element: Optional[Element] = None,
        material: Union["BackgroundState", Material, None] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        self.set_style(style)

        self.layer = None

        self._element: Optional[Element] = None

        self.set_element(element, _update=False)

        super().__init__(
            material,
            rect,
            pos,
            x,
            y,
            size,
            width,
            height,
            content_pos,
            content_x,
            content_y,
            content_size,
            content_w,
            content_h
        )

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
