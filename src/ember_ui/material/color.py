import pygame
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ember_ui.ui.base.element import Element

from ..common import ColorType
from ..material.material import MaterialWithSizeCache


class Color(MaterialWithSizeCache):
    """
    Fills the material area with the specified color.
    """

    def __init__(
        self,
        color: ColorType,
        outline: int = 0,
        alpha: int = 255,
    ):
        super().__init__(alpha)

        self._color: pygame.Color = pygame.Color(color)
        """
        The color of the material. Any format that Pygame supports is accepted.
        """

        self.outline: int = outline
        """
        The thickness of the shape outline. If set to 0, the material will be filled with no outline.
        """

    def __repr__(self) -> str:
        return f"<Color({self._color})>"

    def _needs_to_render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> bool:
        if element not in self._cache:
            return True
        if 0 in self._cache[element].get_size():
            return True
        return (
            self._cache[element].get_size() != size
            or self._cache[element].get_at((0, 0))[:3] != self._color[:-1]
        )

    def _render_surface(
        self,
        element: Optional["Element"],
        surface: Optional[pygame.Surface],
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> Any:
        surface = pygame.Surface((max(0.0, size[0]), max(1.0, size[1])), pygame.SRCALPHA)
        pygame.draw.rect(surface, self._color, (0, 0, *size), self.outline)
        return surface

    def _set_color(self, color: ColorType) -> None:
        self.set_color(color)

    def set_color(self, color: ColorType) -> None:
        self._color = pygame.Color(color)
        self.clear_cache()

    color: ColorType = property(fget=lambda self: self._color, fset=_set_color)


DEFAULT_BLACK_MATERIAL = Color("black")
