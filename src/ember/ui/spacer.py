import pygame
from typing import Union

from .element import Element
from .view import View
from ..size import Size, FILL


class Spacer(Element):
    def __init__(self, size: Union[tuple[Union[Size, int], Union[Size, int]]] = (FILL,FILL),
                 width: int = None, height: int = None):
        if width is not None:
            size = (width, size[1])
        if height is not None:
            size = (size[0], height)
        super().__init__(*size, can_focus=False)

    def _update(self, root: View):
        pass

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):
        pass