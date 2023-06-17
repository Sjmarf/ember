import pygame
from typing import Union, Optional, Sequence, Callable, TYPE_CHECKING

from .. import common as _c
from ..event import BUTTONCLICKED

from ..ui.h_stack import HStack
from ..ui.text import Text
from .base.interactive import Interactive
from .base.element import Element, ElementStrType
from ..ui.load_element import load_element

from ..size import SizeType, SequenceSizeType, SizeMode
from ..position import PositionType, CENTER, SequencePositionType

if TYPE_CHECKING:
    from ..style.button_style import ButtonStyle
    from ..ui.view import ViewLayer

from ..state.state_controller import StateController

from .. import log


class Button(Element, Interactive):
    """
    A Button is an interactive Element. Buttons can hold exactly one child Element, which is rendered on the button.
    When the button is clicked, it will post the :code:`ember.BUTTONCLICKED` event.
    """

    def __init__(
        self,
        *element: Union[Sequence[ElementStrType], ElementStrType],
        can_hold: bool = False,
        hold_delay: float = 0.2,
        hold_start_delay: float = 0.5,
        disabled: bool = False,
        on_click: Optional[Callable[["Button"], None]] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Optional["ButtonStyle"] = None,
    ):
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

        self._style: "ButtonStyle"
        self._min_w: float = 0
        self._min_h: float = 0
        self._hold_timer: float = hold_start_delay
        self._is_held: bool = False

        self._element: Optional[Element] = None

        self.set_style(style)

        Element.__init__(self, rect, pos, x, y, size, width, height)
        Interactive.__init__(self, disabled)
        self.set_element(*element)

    def __repr__(self) -> str:
        return f"<Button({self._element})>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        # Decide which image to draw
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

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        super()._update_rect_chain_down(surface, x, y, w, h)

        with log.size.indent:
            if self._element:
                self._element._update_rect_chain_down(
                    surface,
                    x + w // 2 - self._element.get_abs_width(w) // 2,
                    y + h // 2 - self._element.get_abs_height(h) // 2,
                    self._element.get_abs_width(w),
                    self._element.get_abs_height(h),
                )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._w.mode == SizeMode.FIT:
            if self._element:
                if self._element._w.mode == SizeMode.FILL:
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width Button."
                    )
                self._min_w = self._element.get_abs_width()
            else:
                self._min_w = self._style.size[0]

        if self._h.mode == SizeMode.FIT:
            if self._element:
                if self._element._h.mode == SizeMode.FILL:
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height Button."
                    )
                self._min_h = self._element.get_abs_height()
            else:
                self._min_h = self._style.size[1]

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        if self._element:
            with log.layer.indent:
                self._element._set_layer_chain(layer)

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

    def _set_style(self, style: Optional["ButtonStyle"]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional["ButtonStyle"]) -> None:
        """
        Sets the ButtonStyle of the Button.
        """
        self._style: "ButtonStyle" = self._get_style(style)

    def _set_element(
        self, *element: Union[Sequence[ElementStrType], ElementStrType]
    ) -> None:
        self.set_element(element)

    def set_element(
        self, *element: Union[Sequence[ElementStrType], ElementStrType]
    ) -> None:
        """
        Replace the child element of the Button.
        """
        if not element or element == (None,):
            self._element = None

        else:
            if len(element) > 1:
                self._element: Optional[Element] = HStack(
                    *[
                        load_element(i, text_style=self._style.text_style)
                        for i in element
                    ]
                )

            elif isinstance(element[0], (Element, str)):
                self._element: Optional[Element] = load_element(
                    element[0], text_style=self._style.text_style
                )
            else:
                self._element: Optional[Element] = HStack(
                    *[
                        load_element(i, text_style=self._style.text_style)
                        for i in element[0]
                    ]
                )

            self._element._set_parent(self)
            log.layer.line_break()
            log.layer.info(self, "Element added to Button - starting chain...")
            with log.layer.indent:
                self._element._set_layer_chain(self.layer)

        self._update_rect_chain_up()

    element: Optional[Element] = property(
        fget=lambda self: self._element,
        fset=_set_element,
        doc="The child element of the Button. Synonymous with the set_element() method.",
    )

    style: "ButtonStyle" = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ButtonStyle of the Button. Synonymous with the set_style() method.",
    )
