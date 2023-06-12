import inspect
import pygame
import abc
from typing import Optional, Sequence, Union, TYPE_CHECKING

from ember import common as _c
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType, SequenceSizeType
from ember.position import PositionType, SequencePositionType
from ember.transition.transition import Transition
from ember.state.background_state import BackgroundState
from ember.material.material import Material
from ...size import FIT, FILL, SizeMode

from .container import Container

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer


class SingleElementContainer(Container):
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
    ):
        """
        Base class for Containers that hold one or zero elements. Should not be instantiated directly.
        """
        default_size = self._style.size
        if hasattr(self._style, "sizes") and self._style.sizes is not None:
            for cls in inspect.getmro(type(self)):
                if cls in self._style.sizes:
                    default_size = self._style.sizes[cls]
                    break

        if self._element is not None:
            if not isinstance(default_size, Sequence):
                default_size = default_size, default_size

            if default_size[0] == FIT:
                default_size = (
                    FILL if self._element._w.mode == SizeMode.FILL else FIT,
                    default_size[1],
                )

            if default_size[1] == FIT:
                default_size = (
                    default_size[0],
                    FILL if self._element._h.mode == SizeMode.FILL else FIT,
                )

        super().__init__(material, rect, pos, x, y, size, width, height, default_size=default_size)

    def __getitem__(self, item: int) -> Element:
        if item == 0:
            return self._element
        else:
            return NotImplemented

    def __setitem__(self, key: int, value: Element):
        if key != 0 or not isinstance(value, Element):
            return NotImplemented

        self.set_element(value)

    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        if self._element and self._element.is_visible:
            self._element._render_a(surface, offset, alpha=alpha)

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        self._element._set_layer_chain(layer)

    def _set_element(self, element: Optional[Element]) -> None:
        self.set_element(element)

    def set_element(
        self,
        element: Optional[Element],
        transition: Optional[Transition] = None,
        _update: bool = True,
    ) -> None:
        """
        Replace the element in the Container with a new element.
        """
        if element is not self._element:
            if transition:
                self._transition = transition._new_element_controller()
                self._transition.old = self.copy()
                self._transition.new = self

            self._element: Optional[Element] = element
            if element is not None:
                self._can_focus = element._can_focus
                self._element._set_parent(self)

                log.layer.line_break()
                log.layer.info(self, "Element added to Container - starting chain...")
                with log.layer.indent:
                    self._element._set_layer_chain(self.layer)
            else:
                self._can_focus = False

            if _update:
                log.size.info(self, "Element set, starting chain up...")
                with log.size.indent:
                    self._update_rect_chain_up()

    element = property(
        fget=lambda self: self._element,
        fset=_set_element,
        doc="The element contained within the Container.",
    )
