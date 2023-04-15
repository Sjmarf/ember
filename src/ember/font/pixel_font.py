import pygame

import os

from .base_font import BaseFont, Line


class PixelFont(BaseFont):
    def __init__(self, filename,
                 order="abcdefghijklmnopqrstuvwxyz0123456789: ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       "/_-.?)(,<>%;][—=`\\'éôàèêù!œë+•|", variants=("regular", "underlined", "outlined")):

        self.letters = {}
        self.variants = {}
        self.name = filename

        self.sheet = pygame.image.load(os.path.join(filename, 'font.png')).convert_alpha()

        size = 0
        letter = 0

        for x in range(self.sheet.get_width()):
            if self.sheet.get_at((x, 0)) == (200, 200, 200, 255):
                self.letters[order[letter]] = (x - size, size)
                size = 0
                letter += 1
            else:
                size += 1

        self.letters['\n'] = self.letters[' ']
        self.letters['\r'] = self.letters[' ']

        size = 0
        variant = 0

        for y in range(self.sheet.get_height()):
            if self.sheet.get_at((0, y)) == (200, 200, 200, 255):
                self.variants[variants[variant]] = (y - size, size)
                size = 0
                variant += 1
            else:
                size += 1

        self.y_offset = 1

        self.line_height = self.variants["regular"][1]
        self.line_spacing = 1

        self.cursor = pygame.Surface((max(1, int(self.line_height * 0.07)), self.line_height), pygame.SRCALPHA)
        self.cursor.fill((255, 255, 255))
        self.cursor_offset = (0, 0)

    def get_width_of(self, text):
        return sum(self.letters[i][1] - 5 for i in text) - 1

    def _render_text(self, text, col) -> pygame.Surface:
        surf = pygame.Surface((self.get_width_of(text), self.line_height), pygame.SRCALPHA)
        x = - 3
        for letter in text:
            letter = self.letters[letter]
            letter_surf = self.sheet.subsurface((letter[0], 0, letter[1], self.line_height))
            surf.blit(letter_surf, (x, 0))
            x += letter[1] - 5

        surf.fill(col, special_flags=pygame.BLEND_RGB_ADD)
        return surf
