import pygame
from typing import Union, Optional, Literal

from .base.single_element_container import SingleElementContainer
from .base.element import Element
from .view import ViewLayer
from .base.resizable import Resizable
from ..material.material import Material
from ..state.state_controller import StateController
from ..state.state import State, load_background

from ..size import FIT, FILL, SizeType, SequenceSizeType
from ..position import PositionType
from ..style.container_style import ContainerStyle
from ..style.load_style import load as load_style

from .. import common as _c
from .. import log


class Box(SingleElementContainer, Resizable):
    """
    A Box is a container that can optionally hold one Element.
    """
    def __init__(
        self,
        element: Optional[Element],
        background: Optional[Material] = None,
        focus_self: bool = False,
        resize_edge: Union[
            list[Literal["left", "right", "top", "bottom"]],
            Literal["left", "right", "top", "bottom"],
            None,
        ] = None,
        resize_limits: tuple[int, int] = (50, 300),
        position: PositionType = None,
        size: SequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
        style: Optional[ContainerStyle] = None,
    ):
        self.set_style(style)

        self.background: Optional[State] = load_background(self, background)
        """
        The State to use for the background of the Box. Overrides the states from the ContainerStyle.
        """

        self._fit_width: float = 0
        self._fit_height: float = 0

        super().__init__(
            position,
            size,
            width,
            height,
            default_size=(
                FIT if not element or element._width.mode != 2 else FILL,
                FIT if not element or element._height.mode != 2 else FILL,
            ),
        )

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object is responsible for managing the Box's 
        background states.
        """

        self.focus_self: bool = focus_self
        """
        Modifies how the Box behaves with keyboard / controller navigation. If set to True, the Box itself 
        is focusable. If you press enter when the Box is focused, the child of the Box is focused.
        """

        self.resize_edge: list[str] = (
            [resize_edge] if isinstance(resize_edge, str) else resize_edge
        )
        """
        EXPERIMENTAL. Specify which edge(s) of the Box can be resized by clicking and dragging with the mouse.
        """

        self.resize_limits: tuple[int, int] = resize_limits
        """
        EXPERIMENTAL. Specify limits that the user cannot resize the Box beyond.
        """

        self._hovering_resize_edge = None
        self._resizing = None
        self.set_element(element)

    def __repr__(self) -> str:
        return "<Box>"

    def _update(self) -> None:
        if self._element and self._element.is_visible:
            self._element._update_a()

        if self.resize_edge and not self._resizing:
            self._is_hovering_resizable_edge()

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
            element_x = pos[0] + self.get_abs_width(max_size[0]) / 2 - self._element.get_abs_width(self.rect.w) / 2
            element_y = pos[1] + self.get_abs_height(max_size[1]) / 2 - self._element.get_abs_height(self.rect.h) / 2
            element_w = self._element.get_abs_width(self.rect.w)
            element_h = self._element.get_abs_height(self.rect.h)
                    
            if not self.is_visible:
                self._element.is_visible = False
            elif (
                element_x + element_w < surface.get_abs_offset()[0]
                or element_x
                > surface.get_abs_offset()[0] + surface.get_width()
                or element_y + element_h < surface.get_abs_offset()[1]
                or element_y
                > surface.get_abs_offset()[1] + surface.get_height()
            ):
                self._element.is_visible = False
            else:
                self._element.is_visible = True
            
            self._element._update_rect_chain_down(
                surface, (element_x, element_y),
                self.rect.size,
            )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._height.mode == 1:
            if self._element:
                self._fit_height = self._element.get_abs_height()
            else:
                self._fit_height = 20

        if self._width.mode == 1:
            if self._element:
                self._fit_width = self._element.get_abs_width()
            else:
                self._fit_width = 20

    def _set_layer_chain(self, layer: ViewLayer) -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer: Optional[ViewLayer] = layer
        if self._element is not None:
            self._element._set_layer_chain(layer)

    def _focus_chain(self, previous=None, direction: str = "in") -> Element:
        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

        if direction == "out":
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self
            else:
                log.nav.info(self, f"-> parent {self.parent}.")
                return self.parent._focus_chain(self, direction=direction)
        elif (
            direction in {"up", "down", "left", "right", "forward"}
            or self._element is None
        ):
            return self.parent._focus_chain(self, direction=direction)

        else:
            if self.focus_self:
                log.nav.info(self, "Returning self.")
                return self
            else:
                log.nav.info(self, f"-> child {self._element}.")
                return self._element._focus_chain(None, direction=direction)

    def _event(self, event: pygame.event.Event) -> bool:
        if self._hovering_resize_edge:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._resizing = True
                return True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._resizing = False
                return True

            elif event.type == pygame.MOUSEMOTION and self._resizing:
                self._resize()
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.layer.element_focused is self:
                    log.nav.info(self, "Enter key pressed, starting focus chain.")
                    with log.nav.indent:
                        self.layer._focus_element(self._element)
                    log.nav.info(
                        self,
                        f"Focus chain ended. Focused {self.layer.element_focused}.",
                    )
                    return True

        if self._element is not None:
            return self._element._event(event)
        return False

