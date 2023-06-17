import pygame
from typing import Optional, TYPE_CHECKING
from .material import Material

if TYPE_CHECKING:
    from ..ui.base.element import Element

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
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        return None
