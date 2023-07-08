import inspect
import pygame
import abc
from typing import Optional, Sequence, Union, TYPE_CHECKING

from ember import common as _c
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType, SequenceSizeType, OptionalSequenceSizeType, Size
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)
from ember.transition.transition import Transition
from ember.state.background_state import BackgroundState
from ember.material.material import Material
from ...size import FIT, FILL, SizeMode

from .container import Container

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer
    from ...style.style import Style


class SingleElementContainer(Container):
    def __init__(
        self,
        material: Union[BackgroundState, Material, None],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: Optional[SequenceSizeType],
        w: Optional[SizeType],
        h: Optional[SizeType],
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["Style"] = None,
    ):
        """
        Base class for Containers that hold one or zero elements. Should not be instantiated directly.
        """
        #default_size = self._style.size
        #if hasattr(self._style, "sizes") and self._style.sizes is not None:
            #for cls in inspect.getmro(type(self)):
                #if cls in self._style.sizes:
                    #default_size = self._style.sizes[cls]
                    #break

        #if self._element is not None:
            #if not isinstance(default_size, Sequence):
                #default_size = default_size, default_size

            #if default_size[0] == FIT:
                #default_size = (
                    #FILL if self._element._active_w.mode == SizeMode.FILL else FIT,
                    #default_size[1],
                #)

            #if default_size[1] == FIT:
                #default_size = (
                    #default_size[0],
                    #FILL if self._element._active_h.mode == SizeMode.FILL else FIT,
                #)

        super().__init__(
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            style=style
        )

        if not isinstance(content_size, Sequence):
            content_size = content_size, content_size

        content_w = content_w if content_w is not None else content_size[0]
        content_h = content_h if content_h is not None else content_size[1]

        self.content_w: Optional[Size] = (
            self._style.content_size[0]
            if content_w is None
            else Size._load(content_w)
        )
        self.content_h: Optional[Size] = (
            self._style.content_size[1]
            if content_h is None
            else Size._load(content_h)
        )

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

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        super()._update_rect_chain_down(surface, x, y, w, h)

        if self._element:
            self._element.set_active_w(self.content_w)
            self._element.set_active_h(self.content_h)

            element_x_obj = (
                self._element._x if self._element._x is not None else self.content_x
            )
            element_y_obj = (
                self._element._y if self._element._y is not None else self.content_y
            )

            element_w = (self._element.get_abs_w(w))
            element_h = (self._element.get_abs_h(h))

            element_x = (x + element_x_obj.get(w, element_w))
            element_y = (y + element_y_obj.get(h, element_h))

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
            
            with log.size.indent:
                self._element._update_rect_chain_down(
                    surface, element_x, element_y, element_w, element_h
                )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._element:
            self._min_w = self._element.get_abs_w()
        else:
            self._min_w = 20

        if self._element:
            self._min_h = self._element.get_abs_h()
        else:
            self._min_h = 20

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        if self._element:
            with log.layer.indent:
                self._element._set_layer_chain(layer)

    @property
    def element(self) -> Optional["Element"]:
        return self._element

    @element.setter
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
