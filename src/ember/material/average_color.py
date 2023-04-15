import pygame
from .. import log
from .material import Material
class AverageColor(Material):
    def __init__(self,
                 hsv_adjustment: tuple[int, int, int] = (0, 0, 0)):
        super().__init__()
        self.hsv_adjustment = hsv_adjustment

    def __repr__(self):
        return "<AverageColor({}, {}, {})>".format(*self.hsv_adjustment)

    def render_surface(self, element, surface, pos, size, alpha):
        color = pygame.Color(pygame.transform.average_color(surface, (pos, size)))
        if self.hsv_adjustment:
            hsva = color.hsva

            color.hsva = (max(0, min(360, int(hsva[0] + self.hsv_adjustment[0]) % 360)),
                          max(0, int(min(hsva[1] + self.hsv_adjustment[1], 100))),
                          max(0, int(min(hsva[2] + self.hsv_adjustment[2], 100))), 100)

        if element not in self._cache or (cached_size := self._cache[element].get_size()) != size or \
                self._cache[element].get_at((0, 0)) != color:

            if 0 in size:
                raise ValueError(f"Size {size} cannot be 0.")

            if element not in self._cache:
                log.material.info(self, element,
                                  f"Element not cached, building surface of size {size}...")
            elif self._cache[element].get_at((0, 0)) != color:
                log.material.info(self, element,
                                  f"Cached surface color {self._cache[element].get_at((0, 0))} != "
                                  f"average color {color}, rebuilding surface...")
            elif cached_size != size:  # noqa
                log.material.info(self, element,
                                  f"Cached surface size {cached_size} != size {size}, rebuilding surface...")

            self._cache[element] = pygame.Surface(size, pygame.SRCALPHA)
            self._cache[element].fill(color)
            self._cache[element].set_alpha(alpha)
            return True

        self._cache[element].set_alpha(alpha)
        return False
