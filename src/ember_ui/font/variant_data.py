import time

import pygame
from os import PathLike
from pathlib import Path

from typing import Optional, Union

from .. import log


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

        log.font.info(f"Loaded variant '{self.path.name}' in {time.time() - start_time:2f}s.")


