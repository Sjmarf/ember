import pygame
from typing import Union

from .base.element import Element
from ..size import Size, FILL


class Spacer(Element):
    def __init__(
        self,
        size: Union[tuple[Union[Size, int], Union[Size, int]]] = (0, 0),
        width: int = None,
        height: int = None,
    ):
        if width is not None:
            size = (width, size[1])
        if height is not None:
            size = (size[0], height)
        super().__init__(*size, can_focus=False)

    def __repr__(self) -> str:
        return "<Spacer>"

    def _update(self) -> None:
        pass

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255) -> None:
        pass
