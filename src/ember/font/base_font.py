import abc

import pygame
import array
from typing import Literal, Optional

from ..common import ColorType

from ..position import Position


class Line:
    def __init__(
        self,
        content: str = "",
        start_x: int = 0,
        start_y: int = 0,
        width: int = 0,
        start_index: int = 0,
        line_index: int = 0,
    ):
        self.content = content
        self.start_index = start_index
        self.end_index = self.start_index + len(self.content) - 1
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.line_index = line_index

    def __repr__(self) -> str:
        content = self.content if len(self.content) <= 15 else f"{self.content[:16]}"
        return f"<Line('{content}', start_index={self.start_index})>"

    def __len__(self) -> int:
        return len(self.content)


class BaseFont(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        # Replaced by subclasses
        self.line_height = 0

    def _render_line(
        self,
        surf: pygame.Surface,
        text: str,
        max_width: int,
        y: int,
        height: int,
        color: Optional[ColorType],
        align: Position,
    ) -> (pygame.Surface, int, int):

        old_surf = surf.copy()
        surf = pygame.Surface((max(1, max_width), y + height), pygame.SRCALPHA)
        surf.blit(old_surf, (0, 0))

        new_text = text
        text_surf = self._render_text(new_text, color)
        x = round(align.get(None, max_width, text_surf.get_width()))

        surf.blit(text_surf, (x, y))
        return surf, x, text_surf.get_width()

    @abc.abstractmethod
    def get_width_of(self, text: str) -> int:
        pass

    @abc.abstractmethod
    def _render_text(
        self,
        text: str,
        color: ColorType,
    ) -> pygame.Surface:
        pass

    def render(
        self,
        text: str,
        color: ColorType,
        max_width: Optional[int],
        align: Position,
    ) -> (pygame.Surface, [Line]):

        if max_width is None:
            surf = self._render_text(text, color)
            return surf, (Line(content=text),)

        max_width: int
        max_width -= abs(align.value)

        height = self.line_height

        surf = pygame.Surface(
            (1 if max_width is None else max(1, max_width), height), pygame.SRCALPHA
        )
        y = 0

        lines = []
        letter_n = -1
        last_n = 0

        this_line = ""

        if not text:
            return surf, [
                Line(
                    content="",
                    start_x=int(align.get(None, surf.get_width(), 0))
                )
            ]

        while text:
            letter_n += 1
            try:
                letter = text[letter_n]
            except IndexError:
                break

            this_line += letter
            line_width = self.get_width_of(this_line)

            if line_width > max_width or letter == "\n":
                space_n = letter_n
                new_line = this_line

                # We're over the max limit, so backtrack until we find a space, then create a new line
                if letter == "\n":
                    this_line = this_line[:-1]

                elif len(new_line) > 1:
                    while True:
                        space_n -= 1
                        new_line = new_line[:-1]
                        letter = new_line[-1]
                        if letter == " ":
                            letter_n = space_n
                            this_line = new_line
                            break
                        if len(new_line) <= 1:
                            letter_n -= 1
                            this_line = this_line[:-1]
                            break

                if this_line.endswith(" "):
                    this_line = this_line[:-1]
                surf, start_x, end_x = self._render_line(
                    surf, this_line, max_width, y, height, color, align
                )
                y += height + self.line_spacing
                lines.append(
                    Line(
                        content=this_line,
                        start_x=start_x,
                        width=end_x,
                        start_index=last_n,
                        line_index=len(lines),
                    )
                )
                this_line = ""
                last_n = letter_n + 1

                if letter == "\n" and letter_n == len(text) - 1:
                    surf, start_x, end_x = self._render_line(
                        surf, "", max_width, y, height, color, align
                    )
                    lines.append(
                        Line(
                            content="",
                            start_x=start_x,
                            start_y=y,
                            width=end_x,
                            start_index=last_n,
                            line_index=len(lines),
                        )
                    )

                continue

            if letter_n >= len(text) - 1:
                surf, start_x, end_x = self._render_line(
                    surf, this_line, max_width, y, height, color, align
                )
                lines.append(
                    Line(
                        content=this_line,
                        start_x=start_x,
                        start_y=y,
                        width=end_x,
                        start_index=last_n,
                        line_index=len(lines),
                    )
                )
                break

        # surf.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_ADD)
        return surf, lines
