import pygame
from typing import Union, Optional, TYPE_CHECKING

from .. import common as _c
from .element import Element
from ..utility.timer import BasicTimer
from ..style.slider_style import SliderStyle
from ..style.load_style import load as load_style

from ..material.material import MaterialController

if TYPE_CHECKING:
    from .view import View


class Slider(Element):
    def __init__(self,
                 value: Optional[float] = None,
                 min_value: float = 0,
                 max_value: float = 100,
                 size: Union[tuple[float, float], None] = None,
                 width: Union[float, None] = None,
                 height: Union[float, None] = None,
                 style: Union[SliderStyle, None] = None):

        # Load the SliderStyle object.
        if style is None:
            if _c.default_slider_style is None:
                load_style("plastic", parts=['slider'])
            self.style = _c.default_slider_style
        else:
            self.style = style

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

        super().__init__(self.width, self.height)
        self.handle_width = 0

        self.min_value = min_value
        self.max_value = max_value

        self.is_active = False
        self.is_hovered = False
        self.is_active_keyboard = False

        self.base_material_controller = MaterialController(self)
        self.handle_material_controller = MaterialController(self)

        self.anim = BasicTimer(value if value is not None else min_value)

    def _get_val_from_mouse_x(self, mouse_x):
        x = mouse_x - self.rect.x - self.handle_width / 2
        w = self.rect.w - self.handle_width
        return max(min(x / w * (self.max_value - self.min_value) + self.min_value,
                       self.max_value), self.min_value)

    def _update(self, root: "View"):
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        if self.is_active:
            val = self._get_val_from_mouse_x(_c.mouse_pos[0])
            if (not self.anim.playing and self.anim.val != val) or \
                    (self.anim.playing and self.anim.stop_at != val):
                self.anim.val = val
                self.anim.playing = False

        self.anim.tick()

        if self.is_active_keyboard:
            if not self.anim.playing:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    self.anim.val = max(
                        min(self.anim.val + _c.delta_time * (self.max_value - self.min_value), self.max_value),
                        self.min_value)
                elif keys[pygame.K_LEFT]:
                    self.anim.val = max(
                        min(self.anim.val - _c.delta_time * (self.max_value - self.min_value), self.max_value),
                        self.min_value)

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View", alpha: int = 255):
        rect = self.rect.move(*offset)

        # Draw the base image
        self.base_material_controller.set_material(self.style.images[0])
        self.base_material_controller.render(self, surface, rect.topleft, rect.size, alpha)

        # Draw the handle image
        if root.element_focused is self:
            img_num = 5 if self.is_active or self.is_active_keyboard else 4
        elif self.is_active:
            img_num = 3
        elif self.is_hovered:
            img_num = 2
        else:
            img_num = 1

        self.handle_width = self.rect.h * self.style.handle_width

        self.handle_material_controller.set_material(self.style.images[img_num])
        self.handle_material_controller.render(self, surface, (rect.x +
                                                               (self.anim.val - self.min_value)
                                                               / (self.max_value - self.min_value)
                                                               * (self.rect.w - self.handle_width), rect.y),
                                               (self.handle_width, rect.h), alpha)

    def _event(self, event: int, root: "View"):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_active = True
                self.anim.play(self._get_val_from_mouse_x(_c.mouse_pos[0]), duration=0.2)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_active = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if root.element_focused is self:
                    self.is_active_keyboard = not self.is_active_keyboard

        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
            if root.element_focused is self:
                self.is_active = False

    def _on_unfocus(self):
        self.is_active_keyboard = False

    def _get_value(self):
        return self.anim.val

    def set_value(self, value):
        self.anim.val = value

    value = property(
        fget=_get_value,
        fset=set_value
    )
