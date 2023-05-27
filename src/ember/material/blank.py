import pygame
from typing import Optional
from .material import Material


class Blank(Material):
    def __init__(self):
        """
        A blank Material.
        """
        super().__init__(255)

    def __repr__(self) -> str:
        return "<Blank>"

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
        alpha: int,
    ) -> bool:
        return False
