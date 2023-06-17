import abc
import math

import pygame
import array
from typing import Literal, Optional

from .. import common as _c
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
    def get_width_of_line(self, text: str) -> int:
        pass

    def get_width_of(self, text: str, max_height: float = math.inf) -> int:
        if max_height == math.inf:
            return self.get_width_of_line(text)
        if max_height == 0:
            return 0

        width = 10
        while True:
            width += 1
            if (h := self.get_height_of(text, max_width=width)) <= max_height:
                return width

    def get_height_of(self, text: str, max_width: float) -> int:
        if max_width == 0:
            return 0

        lines = [i for i in self.split_into_lines(text, max_width)]
        return len(lines) * (self.line_height + self.line_spacing) - self.line_spacing

    @abc.abstractmethod
    def _render_text(
        self,
        text: str,
        color: ColorType,
    ) -> pygame.Surface:
        pass

    def split_into_lines(self, text, max_width):
        last_n = 0
        letter_n = -1

        while letter_n < len(text) - 1:
            letter_n += 1
            if letter_n < 0:
                raise _c.Error("internal font error")

            line_width = self.get_width_of_line(text[last_n : letter_n + 1])

            if line_width > max_width or text[letter_n] == "\n":
                letter = text[letter_n]
                space_n = letter_n

                if letter == "\n":
                    this_line = text[last_n : letter_n + 1]

                else:
                    if letter_n - last_n > 1:
                        while True:
                            space_n -= 1
                            if text[space_n] == " ":
                                letter_n = space_n
                                break
                            if space_n - last_n <= 1:
                                letter_n -= 1
                                break

                    this_line = text[last_n : letter_n + 1]

                if this_line.endswith(" "):
                    this_line = this_line[:-1]

                yield last_n, this_line
                last_n = letter_n + 1

                if letter == "\n" and letter_n == len(text) - 1:
                    yield last_n, ""

            if letter_n >= len(text) - 1:
                yield last_n, text[last_n:]

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

        if not text:
            return surf, [
                Line(content="", start_x=int(align.get(None, surf.get_width(), 0)))
            ]

        lines = []
        y = 0

        for index, line in self.split_into_lines(text, max_width):
            surf, start_x, end_x = self._render_line(
                surf, line, max_width, y, height, color, align
            )
            y += height + self.line_spacing
            lines.append(
                Line(
                    content=line,
                    start_x=start_x,
                    width=end_x,
                    start_index=index,
                    line_index=len(lines),
                )
            )
        return surf, lines
