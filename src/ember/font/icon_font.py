import pygame
import difflib
import os
from os import PathLike
from pathlib import Path
from typing import Union, Sequence


class IconFont:
    def __init__(self, path: Union[str, PathLike]):
        if isinstance(path, str):
            path = Path(path)
        self.path: PathLike = path

        self.icon_names = []
        self.layer_names = []

        for i in os.listdir(self.path / "icons"):
            if i.endswith(".png"):
                if not (i.endswith("_b.png") or i.endswith("_c.png")):
                    self.icon_names.append(i[:-4])
                else:
                    self.layer_names.append(i[:-4])

    def get(self, name: str) -> Sequence[pygame.Surface]:
        if name not in self.icon_names:
            msg = f"No icon named '{name}' was found."

            close_matches = difflib.get_close_matches(name, self.icon_names, n=3)
            if close_matches:
                msg += " Did you mean: '" + "', '".join(close_matches) + "'?"

            raise ValueError(msg)

        if f"{name}_b" in self.layer_names:
            if f"{name}_c" in self.layer_names:
                return (
                    pygame.image.load(self.path / f"icons/{name}.png").convert_alpha(),
                    pygame.image.load(
                        self.path / f"icons/{name}_b.png"
                    ).convert_alpha(),
                    pygame.image.load(
                        self.path / f"icons/{name}_c.png"
                    ).convert_alpha(),
                )

            return (
                pygame.image.load(self.path / f"icons/{name}.png").convert_alpha(),
                pygame.image.load(self.path / f"icons/{name}_b.png").convert_alpha(),
            )

        return (pygame.image.load(self.path / f"icons/{name}.png").convert_alpha(),)
