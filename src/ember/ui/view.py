import pygame
from .. import event as ember_event
from .. import common as _c
from .. import log
from ..common import InheritType, INHERIT, RectType
from typing import Optional, TYPE_CHECKING, Any, Sequence, Union, overload

if TYPE_CHECKING:
    from ..style.view_style import ViewStyle
    from ..transition.transition import Transition
    from ember.ui.base.element import Element

from .view_layer import ViewLayer
from ..state.state import StateType

KEY_NAMES = {
    pygame.K_RIGHT: _c.FocusDirection.RIGHT,
    pygame.K_LEFT: _c.FocusDirection.LEFT,
    pygame.K_UP: _c.FocusDirection.UP,
    pygame.K_DOWN: _c.FocusDirection.DOWN,
    pygame.K_TAB: _c.FocusDirection.FORWARD,
}

JOY_HAT_NAMES = {
    (0, 1): _c.FocusDirection.UP,
    (0, -1): _c.FocusDirection.DOWN,
    (-1, 0): _c.FocusDirection.LEFT,
    (1, 0): _c.FocusDirection.RIGHT,
}

DPAD_NAMES = {
    11: _c.FocusDirection.UP,
    12: _c.FocusDirection.DOWN,
    13: _c.FocusDirection.LEFT,
    14: _c.FocusDirection.RIGHT,
}


class View:
    @overload
    def __init__(
        self,
        *layers: Union["ViewLayer", Sequence["ViewLayer"]],
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        element: "Element",
        focused: Optional["Element"] = None,
        keyboard_nav: bool = True,
        material: StateType = None,
        listen_for_exit: Union[InheritType, bool] = INHERIT,
        transition: Union[InheritType, "Transition", None] = INHERIT,
        transition_in: Union[InheritType, "Transition", None] = INHERIT,
        transition_out: Union[InheritType, "Transition", None] = INHERIT,
        style: Optional["ViewStyle"] = None,
    ) -> None:
        ...

    def __init__(
        self,
        *layers: Union["ViewLayer", Sequence["ViewLayer"], "Element"],
        focused: Optional["Element"] = None,
        keyboard_nav: bool = True,
        material: StateType = None,
        listen_for_exit: Union[InheritType, bool] = INHERIT,
        transition: Union[InheritType, "Transition", None] = INHERIT,
        transition_in: Union[InheritType, "Transition", None] = INHERIT,
        transition_out: Union[InheritType, "Transition", None] = INHERIT,
        style: Optional["ViewStyle"] = None,
        element: Optional["Element"] = None,
    ) -> None:
        if not _c.clock:
            raise _c.Error("You must use ember.set_clock() before initialising a view.")

        self.keyboard_nav: bool = keyboard_nav
        """
        Whether keyboard and controller navigation is enabled for this View.
        """

        self._layers: list[ViewLayer] = []

        if isinstance(layers[0], (Sequence, ViewLayer)):
            if isinstance(layers[0], Sequence):
                layers = layers[0]
            for layer in layers:
                self._layers.append(layer)
                layer.view = self
        else:
            if layers:
                element = layers[0]
            self._layers.append(
                ViewLayer(
                    element,
                    focused=focused,
                    material=material,
                    listen_for_exit=listen_for_exit,
                    transition=transition,
                    transition_in=transition_in,
                    transition_out=transition_out,
                    view=self,
                    style=style,
                    exit_on_click_off=False,
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
        rect: Optional[RectType] = None,
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

        if update_positions:
            if rect is None:
                rect = (0, 0, *surface.get_size())

        for layer in self._layers:
            if update_positions:
                layer_w = layer.get_abs_width(rect[2])
                layer_h = layer.get_abs_height(rect[3])

                layer_x = rect[0] + layer._x.get(layer, rect[2], layer_w)

                layer_y = rect[1] + layer._y.get(layer, rect[3], layer_h)

                if layer.clamp:
                    layer_x = pygame.math.clamp(
                        layer_x, rect[0], rect[0] + rect[2] - layer_w
                    )
                    layer_y = pygame.math.clamp(
                        layer_y, rect[1], rect[1] + rect[3] - layer_h
                    )

                if self._prev_rect != rect:
                    log.size.info(
                        self, "View rect changed size, starting chain down..."
                    )
                    layer._chain_down_from = layer._element
                layer._update_rect_chain_down(surface, layer_x, layer_y, layer_w, layer_h)
            if render:
                layer._render_a(surface, alpha)

        self._prev_rect = tuple(rect)

        if update_elements:
            for layer in reversed(self._layers):
                layer._update_a()

                if layer.rect.collidepoint(_c.mouse_pos):
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
                    direction = [_c.FocusDirection.LEFT, _c.FocusDirection.RIGHT][
                        self._joy_axis_motion[0] > 0
                    ]
                elif abs(self._joy_axis_motion[1]) > 0.5:
                    direction = [_c.FocusDirection.UP, _c.FocusDirection.DOWN][
                        self._joy_axis_motion[1] > 0
                    ]
                if direction is not None:
                    self._joystick_cooldown = 1
                    self.shift_focus(direction)

    def event(self, event: pygame.event.Event) -> bool:
        """
        Passes Pygame Events to the View. This should be called for each event in the event stack.
        """
        if event.type == ember_event.VIEWEXITFINISHED:
            if event.layer in self._layers and len(self._layers) > 1:
                self._layers.remove(event.layer)
                log.nav.info(self, f"Removed layer {event.layer}.")

        for n, layer in enumerate(reversed(self._layers)):
            if layer._event(event):
                return True
            if event.type in {
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
            } and layer.rect.collidepoint(_c.mouse_pos):
                break

        if self.keyboard_nav and self._layers:
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
                                layer.element_focused._focus_chain(
                                    _c.FocusDirection.OUT
                                )
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
                        layer.shift_focus(_c.FocusDirection.BACKWARD)
                    else:
                        layer.shift_focus(KEY_NAMES[event.key])

            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    self._joy_axis_motion[0] = event.value
                elif event.axis == 1:
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
        focused: Optional["Element"] = None,
        material: StateType = None,
        listen_for_exit: Union[InheritType, bool] = INHERIT,
        transition: Union[InheritType, "Transition", None] = INHERIT,
        transition_in: Union[InheritType, "Transition", None] = INHERIT,
        transition_out: Union[InheritType, "Transition", None] = INHERIT,
        style: Optional["ViewStyle"] = None,
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
        focused: Optional["Element"] = None,
        material: StateType = None,
        listen_for_exit: Union[InheritType, bool] = INHERIT,
        transition: Union[InheritType, "Transition", None] = INHERIT,
        transition_in: Union[InheritType, "Transition", None] = INHERIT,
        transition_out: Union[InheritType, "Transition", None] = INHERIT,
        element: Optional["Element"] = None,
        style: Optional["ViewStyle"] = None,
    ) -> None:
        if not isinstance(layer, ViewLayer) or element is not None:
            if element is None:
                if layer is None:
                    raise ValueError(
                        "You must provide either a ViewLayer or an Element, not None."
                    )
                element = layer
            layer = ViewLayer(
                element,
                focused=focused,
                material=material,
                listen_for_exit=listen_for_exit,
                transition=transition,
                transition_in=transition_in,
                transition_out=transition_out,
                view=self,
                style=style if style is not None else self._layers[0]._style,
            )
        else:
            layer.view = self

        self._layers.append(layer)
        log.nav.info(self, f"Added layer {layer}.")

    def remove_top_layer(self, transition: Optional["Transition"] = None) -> None:
        """
        Remove the top layer of the View.
        """
        self._layers[-1].start_transition_out(transition=transition)

    def update_elements(self) -> None:
        log.size.info(self, "Starting chain down next tick for all layers...")
        for layer in self._layers:
            layer._chain_down_from = layer._element

    def shift_focus(
        self, direction: _c.FocusDirection, element: Optional["Element"] = None
    ) -> None:
        if self._layers:
            self._layers[-1].shift_focus(direction, element=element)

    def start_transition_in(self, transition: Optional["Transition"] = None) -> None:
        """
        Start transitioning all ViewLayers in.
        """
        for layer in self._layers:
            layer.start_transition_in(transition)

    def start_transition_out(
        self, transition: Optional["Transition"] = None, cause: Any = None, **kwargs
    ) -> None:
        """
        Start transitioning the ViewLayer out. When the transition is finished, an ember.MENUEXIT event will be posted.
        This event will have the 'cause' attribute, the value of which can be specified in the 'cause'
        parameter of this method. You can also specify any other keyword argument(s) - they'll be added to the
        event too.
        """
        self._layers[-1].start_transition_out(transition, cause, **kwargs)

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

    layers: list[ViewLayer] = property(
        fget=lambda self: self._layers, doc="A list of the View's ViewLayers."
    )
