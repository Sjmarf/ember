import pygame
from typing import Union, Sequence, Optional, Any, TYPE_CHECKING

from ..utility.stretch_surface import stretch_surface
from .material import Material

if TYPE_CHECKING:
    from ember_ui.ui.base.element import Element


class Surface(Material):
    """
    A pygame Surface wrapped in a Material.
    """

    def __init__(
        self,
        surface: Union[str, pygame.Surface],
        alpha: int = 255,
    ):
        super().__init__(alpha)
        self.surface: pygame.Surface = (
            pygame.image.load(surface).convert_alpha()
            if isinstance(surface, str)
            else surface
        )
        """
        The surface to render.
        """

    def __repr__(self) -> str:
        return "<StretchedSurface>"

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        new_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.surface.set_alpha(alpha)
        new_surface.blit(
            self.surface,
            (
                size[0] // 2 - self.surface.get_width() // 2,
                size[1] // 2 - self.surface.get_height() // 2,
            ),
        )
        return new_surface

    def draw(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> bool:
        self.surface.set_alpha(alpha)
        surface.blit(
            self.surface,
            (
                pos[0] + size[0] // 2 - self.surface.get_width() // 2,
                pos[1] + size[1] // 2 - self.surface.get_height() // 2,
            ),
        )
        return False
