import pygame
from typing import Optional, TYPE_CHECKING
from ember.style.style import Style
from ember.font.icon_font import IconFont
from ember.common import ColorType
from ember.material.color import Color

from ember.ui.icon import Icon


class IconStyle(Style[Icon]):
    def __init__(self, font: IconFont, color: ColorType = "black"):
        self.font: IconFont = font
        self.material = Color(color)
        super().__init__()

    def _on_become_active(self, element: "Icon", event: Optional[pygame.Event]) -> None:
        element.set_font(self.font)
        element.set_material(self.material)
