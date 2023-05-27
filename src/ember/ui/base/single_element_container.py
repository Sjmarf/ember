import pygame
import abc
from typing import Optional, Sequence, Union

from ember import common as _c
from ember import log
from ember.ui.base.element import Element
from ember.ui.view import ViewLayer
from ember.size import SizeType
from ember.position import PositionType
from ember.transition.transition import Transition


from .container import Container


class SingleElementContainer(Container):
    def __init__(
        self,
        position: PositionType,
        size: Sequence[SizeType],
        width: SizeType,
        height: SizeType,
        default_size: Sequence[SizeType] = (20, 20),
    ):
        """
        Base class for Containers that hold one or zero elements. Should not be instantiated directly.
        """
        super().__init__(position, size, width, height, default_size=default_size)

    def _render_elements(
            self,
            surface: pygame.Surface,
            offset: tuple[int, int],
            alpha: int = 255,
    ) -> None:
        if self._element and self._element.is_visible:
            self._element._render_a(surface, offset, alpha=alpha)

    def _set_layer_chain(self, layer: ViewLayer) -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        self._element._set_layer_chain(layer)

    def _set_element(self, element: Optional[Element]) -> None:
        self.set_element(element)

    def set_element(self, element: Optional[Element]) -> None:
        """
        Replace the element in the Box with a new element.
        """
        self._element: Optional[Element] = element
        if element is not None:
            self._can_focus = element._can_focus
            self._element._set_parent(self)
        else:
            self._can_focus = False

        self._update_rect_chain_up()

    element = property(
        fget=lambda self: self._element,
        fset=_set_element,
        doc="The element contained within the Container.",
    )