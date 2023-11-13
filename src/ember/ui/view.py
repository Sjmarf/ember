import pygame
import time
from .. import event as ember_event
from .. import common as _c
from .. import log
from ..common import DefaultType, DEFAULT, RectType
from typing import Optional, TYPE_CHECKING, Sequence, Union, overload

if TYPE_CHECKING:
    from ember.ui.element import Element

from .view_layer import ViewLayer
from ember.ui.context_manager import ContextManager

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


class View(ContextManager):
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
        listen_for_exit: Union[DefaultType, bool] = DEFAULT,
    ) -> None:
        ...

    def __init__(
        self,
        *layers: Union["ViewLayer", Sequence["ViewLayer"], "Element"],
        focused: Optional["Element"] = None,
        keyboard_nav: bool = True,
        listen_for_exit: Union[DefaultType, bool] = DEFAULT,
        element: Optional["Element"] = None,
    ) -> None:
        if not _c.clock:
            raise _c.Error("You must use ember.set_clock() before initialising a view.")

        self.keyboard_nav: bool = keyboard_nav
        """
        Whether keyboard and controller navigation is enabled for this View.
        """

        self._layers: list[ViewLayer] = []

        if layers and isinstance(layers[0], (Sequence, ViewLayer)):
            if isinstance(layers[0], Sequence):
                layers = layers[0]
            for layer in layers:
                self._layers.append(layer)
                layer.view = self
        else:
            if layers:
                element = layers[0]
            if element is not None:
                self._layers.append(
                    ViewLayer(
                        element,
                        focused=focused,
                        listen_for_exit=listen_for_exit,
                        view=self,
                        exit_on_click_off=False,
                    )
                )

        log.size.info("View created")
        for layer in self._layers:
            log.size.info("Building layer...")
            layer.build()

        self._joystick_cooldown = 0
        self._prev_rect: tuple[float, float, float, float] = (0, 0, 0, 0)
        self._joy_axis_motion: Sequence[int] = [0, 0]

        super().__init__()

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
        display_zoom: Union[DefaultType, int] = DEFAULT,
    ) -> None:
        """
        Update the View. This should be called every tick.
        """
        _c.delta_time = 1 / max(1.0, _c.clock.get_fps())

        mouse = pygame.mouse.get_pos()
        if display_zoom is DEFAULT:
            display_zoom = _c.display_zoom
        _c.mouse_pos = mouse[0] // display_zoom, mouse[1] // display_zoom

        if update_positions:
            if rect is None:
                rect = (0, 0, *surface.get_size())

        for layer in self._layers:
            if update_positions:
                layer_w = layer.get_abs_w(rect[2])
                layer_h = layer.get_abs_h(rect[3])

                layer_x = rect[0] + layer._x.value.get(rect[2], layer_w)
                layer_y = rect[1] + layer._y.value.get(rect[3], layer_h)

                if layer.clamp:
                    layer_x = pygame.math.clamp(
                        layer_x, rect[0], rect[0] + rect[2] - layer_w
                    )
                    layer_y = pygame.math.clamp(
                        layer_y, rect[1], rect[1] + rect[3] - layer_h
                    )

                if self._prev_rect != rect:
                    log.size.line_break()
                    log.size.info(
                        self, "ViewLayer rect changed size, queueing for update."
                    )
                    layer.rect.update(*rect[:])
                    layer._int_rect.update(*rect[:])
                    layer.update_rect_next_tick()

                if layer.rect_update_queue or layer.min_size_update_queue:
                    log.size.line_break()
                    log.size.info(
                        "--------------------- TICK START ---------------------"
                    )
                    i = 0
                    start_time = time.time()
                    if layer.can_focus_update_queue:
                        layer.can_focus_update_queue.sort(key=lambda x: len(x.ancestry), reverse=True)
                        while layer.can_focus_update_queue:
                            element = layer.can_focus_update_queue.pop(0)
                            log.nav.line_break()
                            with log.nav.indent(f"Starting can_focus update for {element}..."):
                                element.update_can_focus()

                    while layer.rect_update_queue or layer.min_size_update_queue:
                        if i > 0:
                            log.size.line_break()
                            log.size.info(
                                "Queues aren't empty, going around again..."
                            )
                            if i > 300:
                                raise _c.Error(
                                    "The maximimum number of ViewLayer updates on a single tick (300) was exceeded."
                                )
                        layer._process_queues(surface)
                        i += 1
                    log.size.line_break()
                    log.size.info(
                        f"Tick finishing.",
                    )
                    log.size.info(
                        "---------------------- TICK END ----------------------"
                    )

            if render:
                layer.render(surface, (0, 0), alpha)

        self._prev_rect = tuple(rect)

        if update_elements:
            for layer in reversed(self._layers):
                layer.update()

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
                log.nav.info(f"Removed layer {event.layer}.", self)

        for n, layer in enumerate(reversed(self._layers)):
            if layer.event(event):
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
                        log.nav.info("Escape key pressed, exiting menu.", self)
                        return layer._exit_pressed()
                    else:
                        if layer.element_focused is None:
                            return False
                        with log.nav.indent("Escape key pressed, moving up one layer.", self):
                            layer._focus_element(
                                layer.element_focused._focus_chain(
                                    _c.FocusDirection.OUT
                                )
                            )
                        log.nav.info(
                            f"Focus chain ended. Focused {layer.element_focused}."
                        )
                        return True

                if event.key in KEY_NAMES.keys():
                    log.nav.line_break()
                    with log.nav.indent("Nav key pressed.", self):
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

    def _attribute_element(self, element: "Element") -> None:
        self.append(element)

    @overload
    def append(
        self,
        element: "Element",
        focused: Optional["Element"] = None,
        listen_for_exit: Union[DefaultType, bool] = DEFAULT,
    ) -> None:
        ...

    @overload
    def append(
        self,
        layer: "ViewLayer",
    ) -> None:
        ...

    def append(
        self,
        layer: Union[ViewLayer, "Element", None] = None,
        focused: Optional["Element"] = None,
        listen_for_exit: Union[DefaultType, bool] = DEFAULT,
        element: Optional["Element"] = None,
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
                listen_for_exit=listen_for_exit,
                view=self,
            )
        else:
            layer.view = self

        self._layers.append(layer)
        log.size.info("Building layer")
        layer.build()
        log.nav.info(f"Added layer {layer}.", self)

    def pop(
        self,
        index: int = -1,
    ) -> ViewLayer:
        """
        Remove and return a layer at an index (default last).
        """
        return self._layers[index]

    def update_elements(self) -> None:
        log.size.info("Starting chain down next tick for all layers...")
        for layer in self._layers:
            layer._chain_down_from = layer._element

    def shift_focus(
        self, direction: _c.FocusDirection, element: Optional["Element"] = None
    ) -> None:
        if self._layers:
            self._layers[-1].shift_focus(direction, element=element)

    def start_manual_update(self) -> None:
        """
        Starts the update chain on the next tick. You shouldn't need to call this manually, it exists incase the
        library misses something.
        """
        for layer in self._layers:
            layer.start_manual_update()

    @property
    def layers(self) -> list[ViewLayer]:
        """
        A list of the View's ViewLayers.
        """
        return self._layers
