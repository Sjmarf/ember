import pygame
import logging
import ember.event
from ember import common as _c
from typing import Optional, Literal, Callable, TYPE_CHECKING
from ember.transition.transition import Transition
from ember.ui.text_field import TextField
from ember.ui.slider import Slider

from ember.ui.element import Element

if TYPE_CHECKING:
    from ember.style.view_style import ViewStyle

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
    def __init__(self,
                 element: Element,
                 focused: Optional[Element] = None,
                 style: Optional["ViewStyle"] = None,

                 keyboard_nav: bool = True,
                 listen_for_exit: bool = True,
                 transition: Optional[Transition] = None,
                 transition_in: Optional[Transition] = None,
                 transition_out: Optional[Transition] = None
                 ):

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self.element_focused = focused
        self.keyboard_nav = keyboard_nav
        self.listen_for_exit = listen_for_exit
        
        self.style = style if style else _c.default_view_style

        if transition_in:
            self.transition_in = transition_in
        elif transition:
            self.transition_in = transition
        elif self.style and self.style.transition_in:
            self.transition_in = self.style.transition_in
        else:
            self.transition_in = None

        if transition_out:
            self.transition_out = transition_out
        elif transition:
            self.transition_out = transition
        elif self.style and self.style.transition_out:
            self.transition_out = self.style.transition_out
        else:
            self.transition_out = None

        self.style = style if style else _c.default_view_style

        self._element = element
        element.parent = self
        element.set_root(self)

        if self.transition_in:
            element.animation = self.transition_in.new_element_controller()
            element.animation.new_element = element

        _c.event_ids = ember.event.__dict__.values()
        self.joystick_cooldown = 0

        self.check_size = True
        self._prev_rect = None
        self._waiting_for_transition_finish = False
        self._block_rendering = False

        self._joy_axis_motion = [0, 0]

        self.rect = pygame.Rect((0,0,0,0))

    def update(self, surface: pygame.Surface, rect: pygame.rect.RectType = None,
               update_positions=True, update_elements=True, render=True):
        if update_positions:
            self._update_positions(surface, rect)
        if update_elements:
            self._element.update_a(root=self)
        if render:
            self._render(surface)

        if self.joystick_cooldown > 0:
            self.joystick_cooldown -= _c.delta_time * 5
            if self.joystick_cooldown < 0:
                self.joystick_cooldown = 0

    def _update_positions(self,
                          surface: pygame.Surface, rect: pygame.rect.RectType = None):
        _c.delta_time = 1 / max(1, _c.clock.get_fps())

        if type(rect) is tuple:
            pos = (rect[0] + rect[2] / 2 - self._element.get_width(rect[2]) / 2,
                   rect[1] + rect[3] / 2 - self._element.get_height(rect[3]) / 2,
                   *rect[2:])
        elif type(rect) is pygame.Rect:
            pos = rect.centerx - self._element.get_width(rect.w) / 2, \
                  rect.centery - self._element.get_height(rect.h) / 2, \
                  *rect.size
        else:
            pos = (surface.get_width() / 2 - self._element.get_width(surface.get_width()) / 2,
                   surface.get_height() / 2 - self._element.get_height(surface.get_height()) / 2,
                   *surface.get_size())

        self.rect.update(pos)

        if self._prev_rect != pos:
            self._prev_rect = pos
            self.check_size = True

        if self.check_size:
            self._element.update_rect(pos[:2], pos[2:], root=self)
            # self.check_size = False

        # Joystick controls
        if self.joystick_cooldown == 0:
            direction = None
            if abs(self._joy_axis_motion[0]) > 0.5:
                direction = ["left", "right"][self._joy_axis_motion[0] > 0]
            elif abs(self._joy_axis_motion[1]) > 0.5:
                direction = ["up", "down"][self._joy_axis_motion[1] > 0]
            if direction:
                self.joystick_cooldown = 1
                self._select_element(direction)

    def _render(self, surface: pygame.Surface):
        if not self._block_rendering:
            self._element.render_a(surface, (0, 0), root=self)

    def event(self, event: pygame.event.Event):
        if event.type == ember.event.TRANSITIONFINISHED:
            if event.element is self._element:
                if self._waiting_for_transition_finish:
                    self._exit_menu()

        if event.type in _c.event_ids:
            return

        if event.type == pygame.KEYDOWN and self.keyboard_nav:
            if event.key == pygame.K_ESCAPE:
                self._exit_pressed()

            if event.key in KEY_NAMES.keys():
                if not (type(self.element_focused) in {Slider, TextField} and self.element_focused.is_active):  # noqa
                    if event.key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self._select_element("backward")
                    else:
                        self._select_element(KEY_NAMES[event.key])

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis in {0, 3}:
                self._joy_axis_motion[0] = event.value
            elif event.axis in {1, 4}:
                self._joy_axis_motion[1] = event.value

        elif event.type == pygame.JOYHATMOTION:
            if event.value in JOY_HAT_NAMES:
                self._select_element(JOY_HAT_NAMES[event.value])

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:  # B as ESC key
                self._exit_pressed()

            elif event.button in DPAD_NAMES:
                self._select_element(DPAD_NAMES[event.button])

        self._element.event(event, self)

    def set_element(self, element: Element):
        self._element = element
        element.set_parent(self)
        element.set_root(self)

    def focus_element(self, element):
        self.element_focused = element

    def start_transition(self, transition: Transition = None):
        if transition or self.transition_out:
            transition = transition if transition else self.transition_out
            self._element.animation = transition.new_element_controller()
            self._element.animation.old_element = self._element

    def _exit_pressed(self):
        if self.element_focused is not None:
            self.element_focused = None
        elif self.listen_for_exit:
            if self.transition_out:
                self.start_transition()
                self._waiting_for_transition_finish = True
            else:
                self._exit_menu()

    def _exit_menu(self):
        self._block_rendering = True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        new_event = pygame.event.Event(ember.event.MENUEXIT, view=self)
        pygame.event.post(new_event)

    def shift_focus(self, direction: Literal['left', 'right', 'up', 'down']):
        self._select_element(direction)

    def _select_element(self, direction):
        if self.element_focused is None:
            logging.debug(f'Selection is None. Selecting {self.element_focused}')
            new_element = self._element.focus(self, None)
        else:
            logging.debug(f'Selecting {self.element_focused}')
            new_element = self.element_focused.focus(self, None, key=direction)

        if self.element_focused is not new_element:
            if self.element_focused is not None:
                self.element_focused.unfocus()
            self.element_focused = new_element

        logging.debug(f'Element selection done. Selected {self.element_focused}')
        event = pygame.event.Event(ember.event.ELEMENTFOCUSED, element=self.element_focused)
        pygame.event.post(event)

        # Determine if the element being selected is inside a VScroll
        if self.element_focused is not None:
            for element in self.element_focused.get_parent_tree():
                if type(element).__name__ == "VScroll":
                    # If the element isn't fully visible in the frame, scroll to that element
                    if not element.rect.contains(self.element_focused.rect):
                        logging.debug("Moving VScroll so that selected element is visible")
                        if self.element_focused.rect.y < element.rect.y:
                            destination = element.scroll.val - element.rect.y + self.element_focused.rect.y - \
                                          element.rect.h + self.element_focused.rect.h
                        else:
                            destination = element.scroll.val - element.rect.y + self.element_focused.rect.y
                        element.scroll.play(stop=min(max(-element.over_scroll[0], destination),
                                                     element._element.rect.h - element.rect.h + element.over_scroll[1]),
                                            duration=0.2)

    def focus(self, root: 'View', previous: Element = None, key: int = 0):
        logging.debug("Selected Root. Selection wasn't changed.")
        return self.element_focused

    def _show_controller_keyboard(self):
        pass

    def keybinds_blocked(self):
        return type(self.element_focused).__name__ == "TextField" and self.element_focused.is_active

    def _get_element(self):
        return self._element

    element = property(
        fget=_get_element,
        fset=set_element
    )
