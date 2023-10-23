import abc
import math

import pygame
from typing import Optional, Sequence

from .. import common as _c

from ember.position.position import Position

from .line import Line
from .variant import TextVariant


class Font(abc.ABC):
    def __init__(
        self,
        line_height: int,
        line_spacing: int,
        cursor: pygame.Surface,
        cursor_offset: Sequence[int],
    ):
        # Attributes are replaced by subclasses
        self.line_height: int = line_height
        self.line_spacing: int = line_spacing
        self.cursor: pygame.Surface = cursor
        self.cursor_offset: Sequence[int] = cursor_offset

    @abc.abstractmethod
    def get_width_of_line(self, text: str, variant: Sequence[TextVariant]) -> int:
        pass

    def get_width_of(
        self, text: str, variant: TextVariant, max_width: float = 0, max_height: float = math.inf
    ) -> int:
        if max_height == math.inf:
            return self.get_width_of_line(text, variant)
        if max_height == 0:
            return 0

        if (w := self.get_width_of_line(text, variant)) < max_width:
            return w

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
    
    def get_layers(self, variant: Sequence[TextVariant]) -> list[int]:
        return [1]

    def split_into_lines(self, text, max_width, variant: Sequence[TextVariant]):
        last_n = 0
        letter_n = -1

        while letter_n < len(text) - 1:
            letter_n += 1
            if letter_n < 0:
                raise _c.Error("internal font error")

            line_width = self.get_width_of_line(text[last_n : letter_n + 1], variant)

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

                if this_line[-1] in {" ", "\n"}:
                    this_line = this_line[:-1]

                yield last_n, this_line
                last_n = letter_n + 1

                #if letter == "\n" and letter_n == len(text) - 1:
                    #yield last_n, ""

            if letter_n >= len(text) - 1:
                yield last_n, text[last_n:]

    @abc.abstractmethod
    def render(
        self,
        text: str,
        variant: Sequence[TextVariant],
        max_width: Optional[int],
        align: Position,
    ) -> tuple[list[pygame.Surface], [Line]]:
        pass