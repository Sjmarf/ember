import time

import pygame
import os
import itertools
from os import PathLike
import json
from pathlib import Path, Path

from typing import Sequence, Optional, Union

from ..common import ColorType
from .base_font import BaseFont
from .variant import TextVariant, BOLD, ITALIC, STRIKETHROUGH, UNDERLINE, OUTLINE
from .. import log

from ..position import Position
from .line import Line


def _load_value(*values):
    for i in values:
        if i is not None:
            return i
    raise ValueError()


def string_to_text_variant(string: str) -> TextVariant:
    if string == "BOLD":
        return BOLD
    if string == "ITALIC":
        return ITALIC
    if string == "STRIKETHROUGH":
        return STRIKETHROUGH
    if string == "UNDERLINE":
        return UNDERLINE
    if string == "OUTLINE":
        return OUTLINE
    raise ValueError(f"No matching text variant for '{string}'.")


class VariantData:
    def __init__(
        self,
        path: Union[str, PathLike],
        characters: str,
        raw_layers: Optional[list[int]],
        separator_color: pygame.Color,
    ):
        if isinstance(path, str):
            path = Path(path)
        self.path: PathLike = path

        self.characters: str = characters
        self.separator_color: pygame.Color = separator_color

        self.surfaces: dict[str, list[pygame.Surface]] = {}
        self.character_sizes: dict[str, tuple[int, int]] = {}

        self.raw_layers: Optional[list[int]] = raw_layers
        self.layers: list[int] = []

        self.has_loaded: bool = False

    def load(
        self,
    ) -> None:
        """
        Read the letters into separate subsurfaces.
        """
        start_time = time.time()
        self.has_loaded = True

        sheet = pygame.image.load(self.path).convert_alpha()

        layer_positions = []

        if self.raw_layers is None:
            raw_layers = [1]

        size = 0
        layer_n = 0

        # Determine whether the author included a separator at y = 0 or not
        start_y = int(sheet.get_at((1, 0)) == self.separator_color)

        for y in range(start_y, sheet.get_height()):
            if y == sheet.get_height() - 1 or sheet.get_at((1, y)) == self.separator_color:
                layer_positions.append((y - size, size))
                size = 0
                layer_n += 1
            else:
                size += 1

        size = 0
        letter = 0

        self.layers = list(abs(i) for i in self.raw_layers)
        layer_count = len(self.layers)

        layer_targets: list[int] = []
        for layer_type in self.raw_layers:
            layer_targets.append(self.layers.index(layer_type))
        layer_data = list(
            zip(range(layer_count), self.raw_layers, layer_targets, layer_positions)
        )

        # Determine whether the author included a separator at x = 0 or not
        start_x = int(sheet.get_at((0, 1)) == self.separator_color)

        # Read the unknown character
        for x in range(start_x, sheet.get_width()):
            if sheet.get_at((x, 1)) == self.separator_color:
                self.surfaces["unknown"] = [None] * layer_count
                self.surfaces["unknown"][0] = sheet.subsurface(
                    (x - size, 0, size, layer_positions[0][1])
                )
                self.character_sizes["unknown"] = (x-size, size)
                break

        # Read the remaining characters
        for x in range(x + 1, sheet.get_width()):
            if sheet.get_at((x, 1)) == self.separator_color:
                if letter >= len(self.characters):
                    break

                output = [None] * layer_count

                for n, layer_type, target, (y, h) in layer_data:
                    subsurf = sheet.subsurface((x - size, y, size, h))
                    if layer_type >= 0:
                        if output[target] is None:
                            output[target] = subsurf
                        else:
                            output[target].blit(subsurf, (0, 0))
                    else:
                        if output[target] is None:
                            raise ValueError(
                                "Cannot use subtraction on PixelFont layer because target layer does not yet exist"
                            )
                        output[target].blit(
                            subsurf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB
                        )

                self.surfaces[self.characters[letter]] = output
                self.character_sizes[self.characters[letter]] = (x - size, size)
                size = 0
                letter += 1
            else:
                size += 1

        if " " in self.surfaces:
            self.surfaces["\n"] = self.surfaces[" "]
            self.surfaces["\r"] = self.surfaces[" "]
            self.character_sizes["\n"] = self.character_sizes[" "]
            self.character_sizes["\r"] = self.character_sizes[" "]

        log.font.info(self, f"Loaded variant '{self.path.name}' in {time.time() - start_time:2f}s.")


class PixelFont(BaseFont):
    def __init__(
        self,
        path: Union[str, PathLike, None] = None,
        files: Optional[list[dict]] = None,
        characters: Optional[str] = None,
        line_spacing: Optional[int] = None,
        cursor: Optional[pygame.Surface] = None,
        cursor_size: Optional[Sequence[int]] = None,
        cursor_offset: Optional[Sequence[int]] = None,
        separator_color: Optional[ColorType] = None,
        character_padding: Optional[Sequence[int]] = None,
        kerning: Optional[int] = None,
    ) -> None:
        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            with open(path / "data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            if separator_color is None:
                if "separator_color" in data:
                    if len(data["separator_color"]) == 3:
                        data["separator_color"].append(255)
                    separator_color = pygame.Color(data["separator_color"])
                else:
                    separator_color = pygame.Color([200, 200, 200, 255])

                if "files" in data:
                    files = data["files"]
        else:
            data = {}
            if separator_color is None:
                separator_color = pygame.Color([200, 200, 200, 255])

            elif not isinstance(separator_color, pygame.Color):
                separator_color = pygame.Color(separator_color)

            files = [{"path": ""}]

        separator_color: pygame.Color

        self.characters: str = (
            characters if characters is not None else data["characters"]
        )
        """
        A string containing every character supported by the PixelFont.
        """

        self.variants: dict[Sequence[TextVariant], VariantData] = {}
        for f in files:
            if "variant" in f:
                variant = tuple(
                    sorted(string_to_text_variant(j.upper()) for j in f["variant"] if j)
                )
            else:
                variant = ()

            raw_layers = f['layers'] if 'layers' in f else (1,)
            self.variants[variant] = VariantData(path / f["path"], self.characters, raw_layers, separator_color)
            if not variant:
                self.variants[variant].load()

        line_height = list(self.variants[()].surfaces.values())[0][0].get_height()

        if cursor is None:
            if cursor_size is None:
                if "cursor_size" in data:
                    cursor_size = data["cursor_size"]
                else:
                    cursor_size = max(1, int(line_height * 0.07)), line_height

            cursor = pygame.Surface((cursor_size[0], cursor_size[1]), pygame.SRCALPHA)

            cursor.fill((255, 255, 255))

        self.character_padding: Sequence[int] = _load_value(
            character_padding, data.get("character_padding"), [0, 0]
        )
        """
        The padding on the left and right of every character in the font sheet.
        """

        self.kerning: int = _load_value(kerning, data.get("kerning"), 1)
        """
        The spacing between characters.
        """

        super().__init__(
            line_height=line_height,
            line_spacing=_load_value(line_spacing, data.get("line_spacing"), 1),
            cursor=cursor,
            cursor_offset=_load_value(cursor_offset, data.get("cursor_offset"), [0, 0]),
        )

    def _read_char(self, char: str) -> str:
        if char in self.characters:
            return char
        elif (x := char.lower()) in self.characters or (
            x := char.upper()
        ) in self.characters:
            return x
        else:
            return "unknown"

    def get_width_of_line(self, text: str, variant: Sequence[TextVariant]) -> int:
        total = 0  # -self.character_padding[0]
        if "variant" in self.variants:
            variant_data = self.variants[variant]
        else:
            variant_data = list(self.variants.values())[0]

        if not variant_data.has_loaded:
            log.font.info(self, "Line width requested, loading variant...")
            with log.font.indent:
                variant_data.load()

        for i in text:
            total += variant_data.character_sizes[self._read_char(i)][1]

        total -= (sum(self.character_padding) - self.kerning) * len(text) - 1
        total += self.kerning + self.character_padding[1]

        return total

    def _render_text(
        self, text: str, width: int, variant_data: VariantData, layer_n: int
    ) -> pygame.Surface:
        surf = pygame.Surface((max(1, width), self.line_height), pygame.SRCALPHA)
        offset = sum(self.character_padding) - self.kerning

        x = 0  # -self.character_padding[0]
        for letter in text:
            surf.blit(variant_data.surfaces[self._read_char(letter)][layer_n], (x, 0))
            x += variant_data.character_sizes[self._read_char(letter)][1] - offset

        return surf

    def _render_line(
        self,
        surfaces: list[pygame.Surface],
        text: str,
        max_width: int,
        y: int,
        height: int,
        variant_data: VariantData,
        align: Position,
    ) -> tuple[int, int]:
        width = self.get_width_of(text, variant_data)

        for n in range(len(variant_data.layers)):
            new_surf = pygame.Surface((max(1, max_width), y + height), pygame.SRCALPHA)
            new_surf.blit(surfaces[n], (0, 0))

            text_surf = self._render_text(text, width, variant_data, n)
            x = round(align.get(max_width, text_surf.get_width()))
            new_surf.blit(text_surf, (x, y))
            surfaces[n] = new_surf

        return x, text_surf.get_width()

    def get_layers(self, variant: Sequence[TextVariant]) -> list[int]:
        if tuple(variant) in self.variants:
            variant_data = self.variants[variant]
        else:
            variant_data = list(self.variants.values())[0]
        if not variant_data.has_loaded:
            log.font.info(self, "Layers requested, loading variant...")
            with log.font.indent:
                variant_data.load()
        return variant_data.layers

    def render(
        self,
        text: str,
        variant: Sequence[TextVariant],
        max_width: Optional[int],
        align: Position,
    ) -> tuple[list[pygame.Surface], [Line]]:
        # Find the VariantData object for the given variant

        if tuple(variant) in self.variants:
            variant_data = self.variants[variant]
        else:
            variant_data = list(self.variants.values())[0]

        if not variant_data.has_loaded:
            log.font.info(self, "Text render requested, loading variant...")
            with log.font.indent:
                variant_data.load()

        if max_width is None:
            width = self.get_width_of_line(text, variant_data)
            surfaces = [self._render_text(text, width, variant_data, layer) for layer in range(len(variant_data.layers))]
            return surfaces, (Line(content=text),)

        max_width: int
        max_width -= abs(align.value)

        height = self.line_height

        surface_width = 1 if max_width is None else max(1, max_width)

        surfaces = [
            pygame.Surface((surface_width, height), pygame.SRCALPHA)
            for _ in variant_data.layers
        ]

        if not text:
            return surfaces, [
                Line(content="", start_x=int(align.get(surface_width, 0)))
            ]

        lines = []
        y = 0

        for index, line in self.split_into_lines(text, max_width, variant):
            start_x, end_x = self._render_line(
                surfaces, line, max_width, y, height, variant_data, align
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
        return surfaces, lines
