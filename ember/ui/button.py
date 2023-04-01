import pygame
from typing import Union, Optional, Sequence

from ember import common as _c
import ember.event
from ember.ui.view import View
from ember.ui.h_stack import HStack
from ember.ui.text import Text
from ember.ui.icon import Icon
from ember.ui.ui_object import Interactive
from ember.ui.element import Element
from ember.ui.load_element import load_element

from ember.style.button_style import ButtonStyle
from ember.style.text_style import TextStyle
from ember.style.load_style import load as load_style
from ember.material.stretched_surface import StretchedSurface

from ember.material.material import MaterialController


class Button(Element, Interactive):
    def __init__(self,
                 *element: Sequence[Union[None, str, Element]],
                 size: Optional[Sequence[int]] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,

                 style: Optional[ButtonStyle] = None,
                 text_style: Optional[TextStyle] = None,

                 disabled: bool = False,
                 can_hold: bool = False,
                 hold_delay: float = 0.2,
                 hold_start_delay: float = 0.5,
                 select_when_clicked: bool = False
                 ):

        self._disabled: bool = disabled
        self._can_hold: bool = can_hold
        self.select_when_clicked: bool = select_when_clicked

        if can_hold:
            self._hold_delay: float = hold_delay
            self._hold_start_delay: float = hold_start_delay
            self._is_held: bool = False
            self._hold_timer: float = hold_start_delay

        self.is_hovered: bool = False
        self.is_clicked: bool = False

        self.set_style(style)

        text_style: TextStyle = self._style.text_style if text_style is None else text_style
        if len(element) == 1:
            self.element = load_element(element[0], text_style=text_style)
        else:
            self.element: Element = HStack(*[load_element(i) for i in element])

        # If None is passed as a size value, then use the first set size. If unavailable, use the style image size.
        if size is None:
            if width is not None:
                self.width = width
            else:
                self.width = self.style.default_size[0]

            if height is not None:
                self.height = height
            else:
                self.height = self.style.default_size[1]

        else:
            self.width, self.height = size

        self.material_controller = MaterialController(self)

        super().__init__(self.width, self.height)

    def __repr__(self):
        return f"Button({self.element})"

    def set_root(self, root):
        self.root = root
        if self.element:
            self.element.set_root(root)

    def update_rect(self, pos, max_size, root: View,
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        super().update_rect(pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

        # Update the element
        if self.element:
            if self.is_clicked:
                offset = self._style.element_clicked_offset
            elif root.element_focused is self:
                offset = self._style.element_highlight_offset
            elif self.is_hovered:
                offset = self._style.element_hover_offset
            else:
                offset = self._style.element_offset
            self.element.update_rect(
                (self.rect.x + self.rect.w // 2 - self.element.get_width(self.rect.w) // 2 + offset[0],
                 self.rect.y + self.rect.h // 2 - self.element.get_height(self.rect.h) // 2 + offset[1]),
                self.rect.size, root)

    def update(self, root: View):
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        # If button is held down, perform action every x seconds
        if self._can_hold and not self._disabled:
            if self.is_clicked:
                self._hold_timer -= _c.delta_time
                if self._hold_timer < 0:
                    self._is_held = True
                    self._hold_timer = self._hold_delay

                    if _c.audio_enabled and not _c.audio_muted:
                        if (s := self._style.sounds[0]) is not None:
                            s.play()
                    self._perform_event()

            else:
                self._hold_timer = self._hold_start_delay

        self.element.update_a(root)

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):
        # Decide which image to draw
        rect = self.rect.move(*offset)
        if self._disabled:
            img_num = 3
        elif self.is_clicked:
            img_num = 5 if root.element_focused is self else 2
        elif root.element_focused is self:
            img_num = 4
        elif self.is_hovered:
            img_num = 1
        else:
            img_num = 0

        self.material_controller.set_material(self._style.images[img_num])
        self.material_controller.render(self, surface,
                                        (rect.x - surface.get_abs_offset()[0],
                                         rect.y - surface.get_abs_offset()[1]),
                                        rect.size, alpha)

        # Draw the element
        if self.element:
            self.element.render_a(surface, offset, root, alpha=alpha)

    def event(self, event: int, root: View):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self._disabled:
            self.is_clicked = self.is_hovered
            if self.is_clicked:
                self._click_down()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered and self.is_clicked and not self._disabled:
                self._click_up()
                if self.select_when_clicked:
                    root.element_focused = self
                    event = pygame.event.Event(ember.event.ELEMENTFOCUSED, element=self)
                    pygame.event.post(event)
            self.is_clicked = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and root.element_focused is self \
                and not self._disabled:
            self.is_clicked = True
            self._click_down()

        elif event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            if root.element_focused is self and not self._disabled:
                self._click_up()
            self.is_clicked = False

        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0 and root.element_focused is self \
                and not self._disabled:
            self.is_clicked = True
            self._click_down()

        elif event.type == pygame.JOYBUTTONUP and event.button == 0:
            if root.element_focused is self and not self._disabled:
                self._click_up()
            self.is_clicked = False

    def _click_down(self):
        if _c.audio_enabled and not _c.audio_muted:
            if (s := self._style.sounds[0]) is not None:
                s.play()

    def _click_up(self):
        if _c.audio_enabled and not _c.audio_muted:
            if (s := self._style.sounds[1]) is not None:
                if (s2 := self._style.sounds[0]) is not None:
                    s2.stop()
                s.play()
        if self._can_hold:
            if self._is_held:
                self._is_held = False
            else:
                self._perform_event()
        else:
            self._perform_event()

    def _perform_event(self):
        text = self.element.text if type(self.element) is Text else None
        icon = self.element.icon if type(self.element) is Icon else None
        event = pygame.event.Event(ember.event.BUTTONCLICKED, element=self, text=text, icon=icon)
        pygame.event.post(event)

    def _set_disabled(self, value: bool):
        self._disabled = value
        self.selectable = not value
        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()
        if self._disabled:
            if self.root:
                if self.root.element_focused is self:
                    self.root.element_focused = None

    def _get_disabled(self):
        return self.disabled

    def _get_style(self):
        return self._style

    def set_style(self, style):
        if style is None:
            if _c.default_button_style is None:
                load_style("plastic", parts=['button'])
            self._style = _c.default_button_style
        else:
            self._style = style

    disabled = property(
        fset=_set_disabled,
        fget=_get_disabled
    )

    style = property(
        fset=set_style,
        fget=_get_style
    )
