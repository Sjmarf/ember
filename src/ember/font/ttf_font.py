import pygame
from typing import Optional

from ..common import ColorType
from ..material import Material


from ..font.base_font import BaseFont, Line
from ..ui.base.element import Element


class Font(BaseFont):
    def __init__(self, font: pygame.font.Font):
        self.font = font

        self.y_offset = 0  # font.get_linesize() / -10

        self.line_height = self.font.size("|")[1]
        self.line_spacing = 3

        self.cursor = pygame.Surface(
            (max(1, int(self.line_height * 0.07)), self.line_height), pygame.SRCALPHA
        )
        self.cursor.fill((255, 255, 255))
        self.cursor_offset = (-self.cursor.get_width() // 2, 0)

    def get_width_of(self, text: str) -> int:
        return self.font.size(text)[0]

    def _render_text(
        self,
        text: str,
        color: ColorType,
    ) -> pygame.Surface:
        return self.font.render(text, True, color)
