import pygame
from typing import Sequence, Optional, Any, TYPE_CHECKING
from .material import MaterialWithElementCache

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class AverageColor(MaterialWithElementCache):
    UPDATES_EVERY_TICK = True
    
    def __init__(self, hsv_adjustment: Sequence[int] = (0, 0, 0), alpha: int = 255):
        super().__init__(alpha)
        self.hsv_adjustment: Sequence[int] = hsv_adjustment

    def __repr__(self) -> str:
        return "<AverageColor({}, {}, {})>".format(*self.hsv_adjustment)

    def get(self, element: "Element") -> Optional[pygame.Surface]:
        return self._cache[element][0]

    def _needs_to_render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> bool:
        color = pygame.Color(pygame.transform.average_color(surface, (pos, size)))
        return (
            element not in self._cache
            or self._cache[element][0].get_size() != size
            or self._cache[element][1] != color
        )

    def _render_surface(
        self,
        element: Optional["Element"],
        surface: Optional[pygame.Surface],
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> Any:
        avg_color = pygame.transform.average_color(surface, (pos, size))
        color = pygame.Color(avg_color)
        if self.hsv_adjustment:
            hsva = color.hsva

            color.hsva = (
                max(0, min(360, int(hsva[0] + self.hsv_adjustment[0]) % 360)),
                max(0, int(min(hsva[1] + self.hsv_adjustment[1], 100))),
                max(0, int(min(hsva[2] + self.hsv_adjustment[2], 100))),
                100,
            )

        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf, avg_color
