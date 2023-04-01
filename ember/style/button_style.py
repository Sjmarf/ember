import pygame
from typing import Union, Optional, Sequence

from ember import common as _c
from ember.style.style import Style, MaterialType
from ember.transition.transition import Transition

from ember.style.text_style import TextStyle

from ember.style.load_material import load_material


class ButtonStyle(Style):
    def __init__(self,
                 default_size: Sequence[int] = (300,80),
                 material: MaterialType = None,
                 click_material: MaterialType = None,
                 hover_material: MaterialType = None,
                 focus_material: MaterialType = None,
                 focus_click_material: MaterialType = None,
                 disabled_material: MaterialType = None,

                 click_down_sound: Optional[pygame.mixer.Sound] = None,
                 click_up_sound: Optional[pygame.mixer.Sound] = None,

                 element_offset: tuple[int, int] = (0, 0),
                 element_hover_offset: tuple[int, int] = (0, 0),
                 element_clicked_offset: tuple[int, int] = (0, 0),
                 element_highlight_offset: tuple[int, int] = (0, 0),

                 text_style: Optional[TextStyle] = None,
                 material_transition: Optional[Transition] = None
                 ):

        material = load_material(material, None)
        hover_material = load_material(hover_material, material)
        focus_material = load_material(focus_material, hover_material)

        self.images = [material,
                       hover_material,
                       load_material(click_material, material),
                       load_material(disabled_material, material),
                       focus_material,
                       load_material(focus_click_material, focus_material),
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

        self.default_size = default_size

    def set_as_default(self):
        _c.default_button_style = self
        return self
