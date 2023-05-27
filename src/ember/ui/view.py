import pygame
from .. import event as ember_event
from .. import common as _c
from .. import log
from ..common import InheritType, INHERIT
from typing import Optional, TYPE_CHECKING, Any, Sequence, Union, overload

from ..style.load_style import load as load_style

if TYPE_CHECKING:
    from ..style.view_style import ViewStyle
    from ..transition.transition import Transition
    from ember.ui.base.element import Element

from .view_layer import ViewLayer
from ..state.state import StateType

KEY_NAMES = {
    pygame.K_RIGHT: "right",
    pygame.K_LEFT: "left",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_TAB: "forward",
}

JOY_HAT_NAMES = {
    (0, 1): "up",
    (0, -1): "down",
    (-1, 0): "left",
    (1, 0): "right",
}

DPAD_NAMES = {
    11: "up",
    12: "down",
    13: "left",
    14: "right",
}


class View:
    @overload
    def __init__(
        self,
        layer: "ViewLayer",
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        element: "Element",
        focused: Optional["Element"] = None,
        keyboard_nav: bool = True,
        background: StateType = None,
        listen_for_exit: bool = True,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
        style: Optional["ViewStyle"] = None,
    ) -> None:
        ...

    def __init__(
        self,
        layer: Union["ViewLayer", "Element", None] = None,
        focused: Optional["Element"] = None,
        keyboard_nav: bool = True,
        background: StateType = None,
        listen_for_exit: bool = True,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
        style: Optional["ViewStyle"] = None,
        element: Optional["Element"] = None,
    ) -> None:
        if not _c.clock:
            raise _c.Error(
                "You must use ember.set_clock() before initialising a view."
            )

        self.keyboard_nav: bool = keyboard_nav
        """
        Whether keyboard and controller navigation is enabled for this View.
        """

        self._layers: list[ViewLayer] = []

        if isinstance(layer, ViewLayer):
            self._layers.append(layer)
        else:
            if layer is not None:
                element = layer
            self._layers.append(
                ViewLayer(
                    element,
                    focused=focused,
                    background=background,
                    listen_for_exit=listen_for_exit,
                    transition=transition,
                    transition_in=transition_in,
                    transition_out=transition_out,
                    view=self,
                    style=style,
                    close_when_click_off=False
                )
            )

        self._joystick_cooldown = 0
        self._prev_rect: tuple[float, float, float, float] = (0, 0, 0, 0)
        self._joy_axis_motion: Sequence[int] = [0, 0]

        _c.views.add(self)

    def __repr__(self) -> str:
        return "<View>"

    def __getitem__(self, item) -> "ViewLayer":
        return self._layers[item]

    def __len__(self) -> int:
        return len(self._layers)

    def update(
        self,
        surface: pygame.Surface,
        rect: pygame.rect.RectType = None,
        update_positions: bool = True,
        update_elements: bool = True,
        render: bool = True,
        alpha: int = 255,
        display_zoom: Union[InheritType, int] = INHERIT,
    ) -> None:
        """
        Update the View. This should be called every tick.
        """
        mouse = pygame.mouse.get_pos()
        if display_zoom is INHERIT:
            display_zoom = _c.display_zoom
        _c.mouse_pos = mouse[0] // display_zoom, mouse[1] // display_zoom

        for layer in self._layers:
            if update_positions:
                layer._update_positions(surface, rect)
            if render:
                layer._render(surface, alpha) 

        for layer in reversed(self._layers):
            if update_elements:
                layer._element._update_a()

            if layer._rect.collidepoint(_c.mouse_pos):
                _c.mouse_pos = (-10, -10)

        _c.mouse_pos = mouse[0] // display_zoom, mouse[1] // display_zoom

        if self._joystick_cooldown > 0:
            self._joystick_cooldown -= _c.delta_time * 5
            if self._joystick_cooldown < 0:
                self._joystick_cooldown = 0

        if update_positions:
            # Joystick controls
            if self._joystick_cooldown == 0:
                direction = None
                if abs(self._joy_axis_motion[0]) > 0.5:
                    direction = ["left", "right"][self._joy_axis_motion[0] > 0]
                elif abs(self._joy_axis_motion[1]) > 0.5:
                    direction = ["up", "down"][self._joy_axis_motion[1] > 0]
                if direction:
                    self._joystick_cooldown = 1
                    self.shift_focus(direction)

    def event(self, event: pygame.event.Event) -> bool:
        """
        Passes Pygame Events to the View. This should be called for each event in the event stack.
        """
        if event.type in _c.event_ids:
            return False

        if event.type == ember_event.MENUEXITFINISHED:
            if event.layer in self._layers and len(self._layers) > 1:
                self._layers.remove(event.layer)
                log.nav.info(self, f"Removed layer {event.layer}.")

        for n, layer in enumerate(reversed(self._layers)):
            if layer._event(event, layer=len(self._layers) - 1 - n):
                return True
            if event.type in {
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
            } and layer._rect.collidepoint(_c.mouse_pos):
                break

        if self.keyboard_nav:
            layer = self._layers[-1]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if layer.element_focused is None:
                        log.nav.info(self, "Escape key pressed, exiting menu.")
                        return layer._exit_pressed()
                    else:
                        if layer.element_focused is None:
                            return False
                        log.nav.info(self, "Escape key pressed, moving up one layer.")
                        with log.nav.indent:
                            layer._focus_element(
                                layer.element_focused._focus_chain(None, "out")
                            )
                        log.nav.info(
                            self, f"Focus chain ended. Focused {layer.element_focused}."
                        )
                        return True

                if event.key in KEY_NAMES.keys():
                    log.nav.info(self, "Nav key pressed.")
                    if (
                        event.key == pygame.K_TAB
                        and pygame.key.get_mods() & pygame.KMOD_SHIFT
                    ):
                        layer.shift_focus("backward")
                    else:
                        layer.shift_focus(KEY_NAMES[event.key])

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis in {0, 3}:
                self._joy_axis_motion[0] = event.value
            elif event.axis in {1, 4}:
                self._joy_axis_motion[1] = event.value

        elif event.type == pygame.JOYHATMOTION:
            if event.value in JOY_HAT_NAMES:
                layer.shift_focus(JOY_HAT_NAMES[event.value])

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:  # B as ESC key
                layer._exit_pressed()

            elif event.button in DPAD_NAMES:
                layer.shift_focus(DPAD_NAMES[event.button])

    @overload
    def add_layer(
        self,
        element: "Element",
        rect: Optional[pygame.rect.RectType] = None,
        focused: Optional["Element"] = None,
        listen_for_exit: bool = True,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
    ) -> None:
        ...

    @overload
    def add_layer(
        self,
        layer: "ViewLayer",
    ) -> None:
        ...

    def add_layer(
        self,
        layer: Union[ViewLayer, "Element", None] = None,
        rect: Optional[pygame.rect.RectType] = None,
        focused: Optional["Element"] = None,
        listen_for_exit: bool = True,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
        element: Optional["Element"] = None,
    ) -> None:
        if not isinstance(layer, ViewLayer) or element:
            if element is None:
                if layer is None:
                    raise ValueError(
                        "You must provide either a ViewLayer or an Element, not None."
                    )
                element = layer
            layer = ViewLayer(
                element,
                focused=focused,
                listen_for_exit=listen_for_exit,
                transition=transition,
                transition_in=transition_in,
                transition_out=transition_out,
                rect=rect,
                view=self,
                style=self._layers[0]._style,
            )
        else:
            layer.view = self
        self._layers.append(layer)
        log.nav.info(self, f"Added layer {layer}.")

    def update_elements(self) -> None:
        log.size.info(self, "Starting chain down next tick for all layers...")
        for layer in self._layers:
            layer._check_size = True

    def shift_focus(self, direction: str) -> None:
        if self._layers:
            self._layers[-1].shift_focus(direction)

    @staticmethod
    def set_focus(element: "Element") -> None:
        element.focus()

    def start_transition_out(
        self, transition: Optional["Transition"] = None, cause: Any = None
    ) -> None:
        self._layers[-1].start_transition_out(transition, cause)

    def _update_rect_chain_up(self) -> None:
        pass

    def _set_style(self, style: Optional["ViewStyle"]) -> None:
        self._layers[0].set_style(style)

    def set_style(self, style: Optional["ViewStyle"]) -> None:
        """
        Sets the ViewStyle of the bottommost ViewLayer.
        """
        self._layers[0].set_style(style)

    style: "ViewStyle" = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ViewStyle of the bottommost ViewLayer. Synonymous with the set_style() method.",
    )

    layers: list[ViewLayer] = property(fget=lambda self: self._layers)
