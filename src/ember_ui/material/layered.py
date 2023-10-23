import pygame
from typing import Optional, TYPE_CHECKING, Union, Sequence
from .material import Material

if TYPE_CHECKING:
    from ..ui.base.element import Element


class Layered(Material):
    def __init__(
        self, *materials: Union[Material, Sequence[Material]], alpha: int = 255
    ):
        """
        A collection of materials layered ontop of one another.
        """
        if isinstance(materials[0], Sequence):
            materials = materials[0]
        self.materials: Sequence[Material] = materials
        super().__init__(alpha)

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        new_surface = pygame.Surface(size, pygame.SRCALPHA)
        for i in self.materials:
            new_surface.blit(
                i.render(
                    element, surface, pos, size, round(alpha / 255 * self.alpha / 255)
                ),
                (0, 0),
            )
        return new_surface

    def draw(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> None:
        for i in self.materials:
            i.draw(element, surface, pos, size, alpha)