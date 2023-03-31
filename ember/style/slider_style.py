import pygame
from typing import Optional, Sequence

from ember import common as _c
from ember.style.style import Style, MaterialType
from ember.material.stretched_surface import StretchedSurface

from ember.style.load_material import load_material


class SliderStyle(Style):
    def __init__(self,
                 default_size: Optional[Sequence[int]] = None,
                 handle_width: Optional[int] = None,

                 base_image: MaterialType = 'pxui/default_styles/plastic/toggle/base.png',
                 default_image: MaterialType = 'pxui/default_styles/plastic/toggle/default.png',
                 click_image: MaterialType = None,
                 hover_image: MaterialType = None,
                 focus_image: MaterialType = None,
                 focus_click_image: MaterialType = None,

                 edge: tuple[int, int, int, int] = (5, 5, 5, 5)):

        default_image = load_material(default_image, None)
        focus_image = load_material(focus_image, default_image)

        self.images = [load_material(base_image, None),
                       default_image,
                       load_material(hover_image, default_image),
                       load_material(click_image, default_image),
                       focus_image,
                       load_material(focus_click_image, focus_image)]

        self.edge = edge

        if default_size is None:
            if isinstance(base_image, StretchedSurface):
                self.default_size = base_image.surface.get_size()
            else:
                self.default_size = (60, 20)
        else:
            self.default_size = default_size

        if handle_width is None:
            if isinstance(base_image, StretchedSurface):
                self.handle_width = default_image.surface.get_width()/default_image.surface.get_height()
            else:
                self.handle_width = 1
        else:
            self.handle_width = handle_width

    def set_as_default(self):
        _c.default_slider_style = self
