import pygame
from typing import Optional, TYPE_CHECKING
from ember.style.style import Style
from ember.font.base_font import BaseFont
from ember.common import ColorType
from ember.material.color import Color
from ember.ui.text import Text

class TextStyle(Style[Text]):
    def __init__(self, font: BaseFont, color: ColorType = "black"):
        self.font: BaseFont = font
        self.material = Color(color)
        super().__init__()

    def _on_become_active(self, element: "Text", event: Optional[pygame.Event]) -> None:
        element.set_font(self.font)
        element.set_material(self.material)
