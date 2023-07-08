import pygame
from typing import Union, Optional, Sequence, Callable, TYPE_CHECKING, Generator

from .. import common as _c
from ..event import BUTTONCLICKED

from ..ui.h_stack import HStack
from ..ui.text import Text
from .base.interactive import Interactive
from .base.element import Element, ElementStrType
from .base.single_element_container import SingleElementContainer
from ..ui.load_element import load_element

from ..size import SizeType, OptionalSequenceSizeType
from ..position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)

if TYPE_CHECKING:
    from ..style.button_style import ButtonStyle
    from ..material.material import Material
    from ..state.button_state import ButtonState
    from ..transition.transition import Transition

from ..state.state_controller import StateController

from .. import log


class Button(SingleElementContainer, Interactive):
    """
    A Button is an interactive Element. Buttons can hold exactly one child Element, which is rendered on the button.
    When the button is clicked, it will post the :code:`ember.BUTTONCLICKED` event.
    """

    def __init__(
        self,
        *element: Union[Sequence[ElementStrType], ElementStrType, Generator[ElementStrType, None, None]],
        can_hold: bool = False,
        hold_delay: float = 0.2,
        hold_start_delay: float = 0.5,
        disabled: bool = False,
        material: Union["ButtonState", "Material", None] = None,
        on_click: Optional[Callable[["Button"], None]] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["ButtonStyle"] = None,
    ):
        self.layer = None

        self.can_hold: bool = can_hold
        """
        If :code:`True`, the button will repeatedly post the :code:`BUTTONCLICKED` event every x 
        seconds whilst the button is held down.
        """

        self.hold_delay: float = hold_delay
        """
        The delay (in seconds) between posting events, if the :code:`can_hold` attribute is :code:`True`.
        """

        self.hold_start_delay: float = hold_start_delay
        """
        The delay (in seconds) between the initial event and the first repeated event, 
        if the :code:`can_hold` attribute is :code:`True`.
        """

        self.is_hovered: bool = False
        """
        Is :code:`True` when the mouse is hovered over the button. Read-only.
        """

        self.is_clicked: bool = False
        """
        Is :code:`True` when the button is clicked down. Read-only.
        """

        self.on_click: Optional[Callable[["Button"], None]] = on_click
        """
        A function to run when the button is clicked.
        """

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object responsible for managing the Button's states.
        """

        self._hold_timer: float = hold_start_delay
        self._is_held: bool = False
        
        self._element: Optional[Element] = None

        SingleElementContainer.__init__(
            self,
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            content_pos,
            content_x,
            content_y,
            content_size,
            content_w,
            content_h,
            style
        )
        Interactive.__init__(self, disabled)
        self.set_element(*element, _update=False)

        log.size.line_break()
        log.size.info(self, "Button created, starting chain up...")
        with log.size.indent:
            self._update_rect_chain_up()

    def __repr__(self) -> str:
        return f"<Button({self._element})>"

    def _render_background(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        rect = self._int_rect.move(*offset)
        self.state_controller.set_state(
            self.style.state_func(self), transitions=(self._style.material_transition,)
        )

        offset2 = self.state_controller.current_state.get_offset(self.state_controller)
        offset = (offset[0] + offset2[0], offset[1] + offset2[1])

        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0] + offset[0],
                rect.y - surface.get_abs_offset()[1] + offset[1],
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
        if self._element:
            offset2 = self.state_controller.current_state.get_element_offset(
                self.state_controller
            )

            self._element._render_a(
                surface, (offset[0] + offset2[0], offset[1] + offset2[1]), alpha=alpha
            )

    def _update(self) -> None:
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        # If button is held down, perform action every x seconds
        if self.can_hold and not self._disabled:
            if self.is_clicked:
                self._hold_timer -= _c.delta_time
                if self._hold_timer < 0:
                    self._is_held = True
                    self._hold_timer = self.hold_delay

                    if _c.audio_enabled and not _c.audio_muted:
                        if (s := self._style.click_down_sound) is not None:
                            s.play()
                    self._post_event()

            else:
                self._hold_timer = self.hold_start_delay

        if self._element:
            self._element._update_a()

    def _event(self, event: pygame.event.Event) -> bool:
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and not self._disabled
        ):
            self.is_clicked = self.is_hovered
            if self.is_clicked:
                self._click_down()
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_clicked:
                self.is_clicked = False
                if self.is_hovered and not self._disabled:
                    self._click_up()
                    return True

        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_RETURN
            and self.layer.element_focused is self
            and not self._disabled
        ):
            self.is_clicked = True
            self._click_down()
            return True

        elif event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            if self.is_clicked:
                self.is_clicked = False
                if self.layer.element_focused is self and not self._disabled:
                    self._click_up()
                    return True

        elif (
            event.type == pygame.JOYBUTTONDOWN
            and event.button == 0
            and self.layer.element_focused is self
            and not self._disabled
        ):
            self.is_clicked = True
            self._click_down()
            return True

        elif event.type == pygame.JOYBUTTONUP and event.button == 0:
            if self.is_clicked:
                self.is_clicked = False
                if self.layer.element_focused is self and not self._disabled:
                    self._click_up()
                    return True

        return False

    def _click_down(self) -> None:
        """
        Called when the Button is clicked down. For internal use only.
        """
        if _c.audio_enabled and not _c.audio_muted:
            if (s := self._style.click_down_sound) is not None:
                s.play()

    def _click_up(self) -> None:
        """
        Called when the Button is clicked up. For internal use only.
        """
        if _c.audio_enabled and not _c.audio_muted:
            if (s := self._style.click_up_sound) is not None:
                if (s2 := self._style.click_down_sound) is not None:
                    s2.stop()
                s.play()
        if self.can_hold:
            if self._is_held:
                self._is_held = False
            else:
                self._post_event()
        else:
            self._post_event()

    def _post_event(self) -> None:
        """
        Posts the BUTTONCLICKED event. For internal use only.
        """
        if self.on_click is not None:
            self.on_click(self)

        text = self._element.text if isinstance(self._element, Text) else None
        event = pygame.event.Event(BUTTONCLICKED, element=self, text=text)
        pygame.event.post(event)

    @property
    def element(self) -> Optional["Element"]:
        return self._element

    @element.setter
    def element(
        self, *element: Union[None, ElementStrType, Sequence[ElementStrType]]
    ) -> None:
        self.set_element(element)

    def set_element(
        self,
        *element: Union[None, ElementStrType, Sequence[ElementStrType], Generator[ElementStrType, None, None]],
        transition: Optional["Transition"] = None,
        _update: bool = True,
    ) -> None:
        """
        Replace the child element of the Button.
        """

        if element:
            if not isinstance(element[0], str) and isinstance(element[0], (Sequence, Generator)):
                element = list(element[0])
                if not element:
                    element = (None,)

        else:
            element = (None,)

        if element[0] is not self._element:
            if transition:
                self._transition = transition._new_element_controller()
                self._transition.old = self.copy()
                self._transition.new = self

            self._element: Optional[Element]

            if len(element) > 1:
                self._element = HStack(
                    *[
                        load_element(i, text_style=self._style.text_style)
                        for i in element
                    ]
                )

            elif isinstance(element[0], (Element, str)):
                self._element = load_element(
                    element[0], text_style=self._style.text_style
                )

            if element is not None:
                self._element._set_parent(self)
                log.layer.line_break()
                log.layer.info(self, "Element added to Button - starting chain...")
                with log.layer.indent:
                    self._element._set_layer_chain(self.layer)

            if _update:
                log.size.info(self, "Element set, starting chain up...")
                with log.size.indent:
                    self._update_rect_chain_up()
