import pygame
from typing import Optional

from ember import common as _c
from ember.style.style import Style, MaterialType

from ember.style.load_material import load_material


class ToggleStyle(Style):
    def __init__(self,
                 base_image: MaterialType = 'pxui/default_styles/plastic/toggle/base.png',
                 default_image: MaterialType = 'pxui/default_styles/plastic/toggle/default.png',
                 hover_image: MaterialType = None,
                 highlight_image: MaterialType = None,

                 switch_on_sound: Optional[pygame.mixer.Sound] = None,
                 switch_off_sound: Optional[pygame.mixer.Sound] = None,

                 edge: tuple[int, int, int, int] = (5, 5, 5, 5)):

        default_image = load_material(default_image, None)
        self.images = [load_material(base_image, None),
                       default_image,
                       load_material(hover_image, default_image),
                       load_material(highlight_image, default_image)]

        self.edge = edge

        if _c.audio_enabled:
            self.sounds = [pygame.mixer.Sound(i) if i else None for i in (switch_on_sound, switch_off_sound)]
        else:
            self.sounds = None

    def set_as_default(self):
        _c.default_toggle_style = self
