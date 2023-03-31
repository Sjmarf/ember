import pygame
from typing import Union, Optional

from ember import common as _c
from ember.style.style import Style, MaterialType
from ember.transition.transition import Transition

from ember.style.text_style import TextStyle

from ember.style.load_material import load_material


class ButtonStyle(Style):
    def __init__(self,
                 default_image: MaterialType = None,
                 click_image: MaterialType = None,
                 hover_image: MaterialType = None,
                 highlight_image: MaterialType = None,
                 highlight_clicked_image: MaterialType = None,
                 disabled_image: MaterialType = None,

                 click_down_sound: Optional[pygame.mixer.Sound] = None,
                 click_up_sound: Optional[pygame.mixer.Sound] = None,

                 element_offset: tuple[int, int] = (0, 0),
                 element_hover_offset: tuple[int, int] = (0, 0),
                 element_clicked_offset: tuple[int, int] = (0, 0),
                 element_highlight_offset: tuple[int, int] = (0, 0),

                 text_style: Optional[TextStyle] = None,
                 material_transition: Optional[Transition] = None
                 ):

        default_image = load_material(default_image, None)
        hover_image = load_material(hover_image, default_image)
        highlight_image = load_material(highlight_image, hover_image)

        self.images = [default_image,
                       hover_image,
                       load_material(click_image, default_image),
                       load_material(disabled_image, default_image),
                       highlight_image,
                       load_material(highlight_clicked_image, highlight_image),
                       ]

        if _c.audio_enabled:
            self.sounds = [pygame.mixer.Sound(i) if i else None for i in (click_down_sound, click_up_sound)]
        else:
            self.sounds = None

        self.element_offset = element_offset
        self.element_hover_offset = element_hover_offset
        self.element_highlight_offset = element_highlight_offset
        self.element_clicked_offset = element_clicked_offset

        self.text_style = text_style
        self.material_transition = material_transition

    def set_as_default(self):
        _c.default_button_style = self
        return self
