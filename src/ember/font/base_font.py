import pygame
from typing import Literal


class Line:
    def __init__(self,
                 content: str = "",
                 start_x: int = 0,
                 start_y: int = 0,
                 width: int = 0,
                 start_index: int = 0,
                 line_index: int = 0):
        self.content = content
        self.start_index = start_index
        self.end_index = self.start_index + len(self.content) - 1
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.line_index = line_index

    def __repr__(self):
        content = self.content if len(self.content) <= 15 else f"{self.content[:16]}"
        return f"<Line('{content}', start_index={self.start_index})>"

    def __len__(self):
        return len(self.content)


class BaseFont:
    def _render_line(self, surf, text, max_width, y, height, col, align):
        old_surf = surf.copy()
        surf = pygame.Surface((max(1, max_width), y + height), pygame.SRCALPHA)
        surf.blit(old_surf, (0, 0))

        new_text = text
        text_surf = self._render_text(new_text, col)
        if align == "left":
            x = 0
        elif align == "center":
            x = max_width / 2 - text_surf.get_width() / 2
        else:
            x = max_width - text_surf.get_width()

        surf.blit(text_surf, (x, y))
        return surf, x, text_surf.get_width()

    def render(self, text, col=(255, 255, 255), max_width=None,
               align: Literal["left", "center", "right"] = "center", **kwargs):
        if max_width is None:
            surf = self._render_text(text, col)
            return surf, (Line(content=text),)

        height = self.line_height

        surf = pygame.Surface((1 if max_width is None else max(1, max_width), height), pygame.SRCALPHA)
        y = 0

        lines = []
        letter_n = -1
        last_n = 0

        this_line = ""

        if not text:
            return surf, [Line(content="", start_x=surf.get_width()//2 if align == "center" else 0)]

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

                surf, start_x, end_x = self._render_line(surf, this_line, max_width, y, height, col, align)
                y += height + self.line_spacing
                lines.append(Line(content=this_line,
                                  start_x=start_x,
                                  width=end_x,
                                  start_index=last_n,
                                  line_index=len(lines)
                                  ))
                this_line = ""
                last_n = letter_n + 1

                if letter == "\n" and letter_n == len(text) - 1:
                    surf, start_x, end_x = self._render_line(surf, "", max_width, y, height, col, align)
                    lines.append(Line(content="",
                                      start_x=start_x,
                                      start_y=y,
                                      width=end_x,
                                      start_index=last_n,
                                      line_index=len(lines)
                                      ))

                continue

            if letter_n >= len(text) - 1:
                surf, start_x, end_x = self._render_line(surf, this_line, max_width, y, height, col, align)
                lines.append(Line(content=this_line,
                                  start_x=start_x,
                                  start_y=y,
                                  width=end_x,
                                  start_index=last_n,
                                  line_index=len(lines)
                                  ))
                break

        # surf.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_ADD)
        return surf, lines
