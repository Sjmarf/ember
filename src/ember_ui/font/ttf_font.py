import pygame
from typing import Optional, Union, TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    import pathlib.Path


from ..font.base_font import Font, Line
from .variant import TextVariant, BOLD, ITALIC, UNDERLINE

from ember.position.position import Position


class PygameFont(Font):
    def __init__(
        self,
        font: Union[pygame.font.Font, str, "pathlib.Path"],
        size: int = 0,
        antialias: bool = True,
        line_height: Optional[int] = None,
        line_spacing: int = 3,
        cursor: Optional[pygame.Surface] = None,
        cursor_offset: Optional[Sequence[int]] = None,
    ) -> None:
        self._font: pygame.font.Font

        if isinstance(font, pygame.font.Font):
            self._font = font
        elif isinstance(font, str) and "." not in font:
            self._font = pygame.font.SysFont(font, size)
        else:
            self._font = pygame.font.Font(font, size)

        self.antialias: bool = antialias

        line_height = self._font.size("|")[1] if line_height is None else line_height
        if cursor is None:
            cursor = pygame.Surface(
                (max(1, int(line_height * 0.07)), line_height),
                pygame.SRCALPHA,
            )
            cursor.fill((255, 255, 255))

        super().__init__(
            line_height=line_height,
            line_spacing=line_spacing,
            cursor=cursor,
            cursor_offset=(
                [-cursor.get_width() // 2, 0]
                if cursor_offset is None
                else cursor_offset
            ),
        )

    def get_width_of_line(self, text: str, variant: Sequence[TextVariant]) -> int:
        self._font.bold = BOLD in variant
        self._font.italic = ITALIC in variant
        self._font.underline = UNDERLINE in variant
        return self._font.size(text)[0]

    def _render_text(
        self,
        text: str,
        variant: Sequence[TextVariant],
    ) -> pygame.Surface:
        return self._font.render(text, self.antialias, "black")

    def _render_line(
        self,
        surf: pygame.Surface,
        text: str,
        max_width: int,
        y: int,
        height: int,
        variant: Sequence[TextVariant],
        align: Position,
    ) -> (pygame.Surface, int, int):
        old_surf = surf.copy()
        surf = pygame.Surface((max(1, max_width), y + height), pygame.SRCALPHA)
        surf.blit(old_surf, (0, 0))

        new_text = text
        text_surf = self._render_text(new_text, variant)
        x = round(align.get(max_width, text_surf.get_width()))

        surf.blit(text_surf, (x, y))
        return surf, x, text_surf.get_width()

    def render(
        self,
        text: str,
        variant: Sequence[TextVariant],
        max_width: Optional[int],
        align: Position,
    ) -> tuple[list[pygame.Surface], [Line]]:
        self._font.bold = BOLD in variant
        self._font.italic = ITALIC in variant
        self._font.underline = UNDERLINE in variant

        if max_width is None:
            surf = self._render_text(text, variant)
            return [surf], (Line(content=text),)

        max_width: int
        max_width -= abs(align.value)

        height = self.line_height

        surf = pygame.Surface(
            (1 if max_width is None else max(1, max_width), height), pygame.SRCALPHA
        )

        if not text:
            return surf, [Line(content="", start_x=int(align.get(surf.get_width(), 0)))]

        lines = []
        y = 0

        for index, line in self.split_into_lines(text, max_width, variant):
            surf, start_x, end_x = self._render_line(
                surf, line, max_width, y, height, variant, align
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
        return [surf], lines
