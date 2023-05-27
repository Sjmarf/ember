import pygame
from typing import Union, Optional, Literal

from .style import Style
from . import defaults
from ..font import Font, BaseFont
from .. import common as _c
from ..common import ColorType

class TextStyle(Style):
    def __init__(self,
                 font: Optional[BaseFont] = None,
                 variant: str = "regular",
                 align: str = "center",
                 color: ColorType = (255, 255, 255),
                 outline_color: ColorType = (0,0,0)):

        self.variant: str = variant
        self.color: ColorType = color
        self.outline_color: ColorType = outline_color
        self.align: str = align

        self.font: BaseFont = Font(pygame.font.SysFont("arial",20)) if font is None else font

    def set_as_default(self) -> "TextStyle":
        defaults.text = self
        return self
