import pygame
import logging
from typing import Union

from ember import common as _c
import ember.event
from ember.ui.element import Element
from ember.utility.timer import BasicTimer
from ember.ui.view import View
from ember.ui.text import Text
from ember.ui.icon import Icon
from ember.style.button_style import ButtonStyle
from ember.style.load_style import load as load_style


class Toggle(Element):
    def __init__(self, active: bool = False, size: Union[tuple[float, float], None] = None,
                 width: Union[float, None] = None, height: Union[float, None] = None,
                 style: Union[ButtonStyle, None] = None, action=None):

        # Load the ToggleStyle object.
        if style is None:
            if _c.default_toggle_style is None:
                load_style("plastic", parts=['toggle'])
            self.style = _c.default_toggle_style
        else:
            self.style = style

        # If None is passed as a size value, then use the first set size. If unavailable, use the style image size.
        if size is None:
            if width is not None:
                self.width = width
            else:
                self.width = self.style.images[0].surface.get_width()

            if height is not None:
                self.height = height
            else:
                self.height = self.style.images[0].surface.get_height()
        else:
            self.width, self.height = size

        super().__init__(self.width, self.height)
        self.handle_width = 0
        self.active = active

        self.anim = BasicTimer(self.style.images[0].surface.get_width() - self.style.images[1].surface.get_width()
                               if self.active else 0)

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        super().update_rect(pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

    def update(self, root: View):
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)
        self.anim.tick()

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):
        rect = self.rect.move(*offset)

        # Draw the base image
        self.style.images[0].render(self, surface, rect.topleft, rect.size, alpha)

        # Draw the handle image
        if root.element_focused is self:
            img_num = 3
        elif self.is_hovered:
            img_num = 2
        else:
            img_num = 1

        self.handle_width = self.style.images[img_num].surface.get_width() / \
                            self.style.images[img_num].surface.get_height() * rect.h

        self.style.images[img_num].render(self, surface, (rect.x + self.anim.val, rect.y),
                                                  (self.handle_width, rect.h), alpha)

    def set_active(self, state: bool, play_sound: bool = False):
        self.active = state
        self.anim.play(stop=(self.width.value - self.handle_width if self.active else 0),
                       duration=0.1)

        event = pygame.event.Event(ember.event.TOGGLECLICKED, element=self, active=self.active)
        pygame.event.post(event)

        if _c.audio_enabled and not _c.audio_muted and play_sound:
            sound = self.style.sounds[not self.active]
            if sound is not None:
                sound.play()

    def event(self, event: int, root: View):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.set_active(not self.active, play_sound=True)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if root.element_focused is self:
                self.set_active(not self.active, play_sound=True)

        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
            if root.element_focused is self:
                self.set_active(not self.active, play_sound=True)
