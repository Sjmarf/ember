import pygame
from typing import Optional, TYPE_CHECKING
from .material import Material

if TYPE_CHECKING:
    from ..base.element import Element


class Blank(Material):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

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
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        return None
