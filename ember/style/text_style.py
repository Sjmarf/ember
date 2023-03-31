import pygame
from typing import Union, Optional, Literal

from ember.style.style import Style
from ember.font import Font, PixelFont
from ember import common as _c

class TextStyle(Style):
    def __init__(self,
                 font: Optional[Union[Font, PixelFont]] = None,
                 variant: str = "regular",
                 align: Literal["left", "center", "right"] = "center",
                 color: Union[str, tuple[int, int, int], pygame.Color, None] = (255, 255, 255),
                 outline_color: Union[str, tuple[int, int, int], pygame.Color, None] = (0,0,0)):

        self.variant = variant
        self.color = color
        self.outline_color = outline_color
        self.align = align

        self.font = Font(pygame.font.SysFont("arial",20)) if font is None else font

    def set_as_default(self):
        _c.default_text_style = self
