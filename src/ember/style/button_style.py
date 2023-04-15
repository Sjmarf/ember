import pygame
from typing import Union, Optional, Sequence

from .. import common as _c
from .style import Style, MaterialType
from ..transition.transition import Transition

from .text_style import TextStyle

from .load_material import load_material, load_sound

from ..size import SizeType

from ..material.material import Material


class ButtonStyle(Style):
    def __init__(self,
                 default_size: Sequence[SizeType] = (300, 80),

                 material: MaterialType = None,
                 hover_material: MaterialType = None,
                 click_material: MaterialType = None,
                 focus_material: MaterialType = None,
                 focus_click_material: MaterialType = None,
                 disabled_material: MaterialType = None,

                 click_down_sound: Union[pygame.mixer.Sound, str, None] = None,
                 click_up_sound: Union[pygame.mixer.Sound, str, None] = None,

                 element_offset: tuple[int, int] = (0, 0),
                 element_hover_offset: tuple[int, int] = (0, 0),
                 element_clicked_offset: tuple[int, int] = (0, 0),
                 element_highlight_offset: tuple[int, int] = (0, 0),

                 text_style: Optional[TextStyle] = None,
                 material_transition: Optional[Transition] = None
                 ):

        self.default_size: Sequence[SizeType] = default_size

        self._material: Material = load_material(material, None)
        self._hover_material: Material = load_material(hover_material, self._material)
        self._click_material: Material = load_material(click_material, self._hover_material)
        self._focus_material: Material = load_material(focus_material, self._hover_material)
        self._focus_click_material: Material = load_material(focus_click_material, self._click_material)
        self._disabled_material: Material = load_material(disabled_material, self._material)

        if _c.audio_enabled:
            self.click_down_sound: Optional[pygame.mixer.Sound] = load_sound(click_down_sound)
            self.click_up_sound: Optional[pygame.mixer.Sound] = load_sound(click_up_sound)
        else:
            self.click_down_sound: Optional[pygame.mixer.Sound] = None
            self.click_up_sound: Optional[pygame.mixer.Sound] = None

        self.element_offset: tuple[int, int] = element_offset
        self.element_hover_offset: tuple[int, int] = element_hover_offset
        self.element_highlight_offset: tuple[int, int] = element_highlight_offset
        self.element_clicked_offset: tuple[int, int] = element_clicked_offset

        self.text_style: TextStyle = text_style
        self.material_transition: Optional[Transition] = material_transition

    def set_as_default(self) -> "ButtonStyle":
        _c.default_button_style = self
        return self

    material = property(
        fget=lambda self: self._material,
        fset=lambda self, value: setattr(self, "_material", load_material(value, None))
    )

    hover_material = property(
        fget=lambda self: self._hover_material,
        fset=lambda self, value: setattr(self, "_hover_material", load_material(value, None))
    )

    click_material = property(
        fget=lambda self: self._click_material,
        fset=lambda self, value: setattr(self, "_click_material", load_material(value, None))
    )

    focus_material = property(
        fget=lambda self: self._focus_material,
        fset=lambda self, value: setattr(self, "_focus_material", load_material(value, None))
    )

    focus_click_material = property(
        fget=lambda self: self._focus_click_material,
        fset=lambda self, value: setattr(self, "_focus_click_material", load_material(value, None))
    )

    disabled_material = property(
        fget=lambda self: self._disabled_material,
        fset=lambda self, value: setattr(self, "_disabled_material", load_material(value, None))
    )


