import pygame
import warnings
from .material import Material
from typing import Optional, Literal

from .. import common as _c

try:
    from PIL import Image, ImageFilter

    pillow_installed = True
except ModuleNotFoundError:
    pillow_installed = False


class Blur(Material):
    def __init__(self,
                 radius: int = 7,
                 method: Optional[Literal["pil", "pygame"]] = "pygame",
                 recalculate_each_tick: bool = False):
        self.radius = radius
        self.recalculate_each_tick = recalculate_each_tick

        ver = pygame.version.vernum
        if not _c.is_ce:
            msg = "You are using the upstream version of Pygame, which does not support blurring. " \
                  "\n\nTo fix this, install pygame-ce by running 'pip uninstall pygame' followed by " \
                  "'pip install pygame-ce'."
            if pillow_installed:
                if method == "pygame":
                    warnings.warn(f"{msg} In the meantime, PIL blur will be used instead.")
                    method = "pil"
            else:
                warnings.warn(f"{msg} In the meantime, parts of the program that "
                              f"should have been blurred will not be blurred.")
                method = None

        elif not (ver[0] >= 2 and ver[1] >= 2):
            msg = "You are using an outdated version of pygame-ce, which does not support blurring. " \
                  "\n\nTo fix this, " \
                  "upgrade pygame-ce to version 2.2.0 or later using 'pip install pygame-ce --upgrade'."

            if pillow_installed:
                if method == "pygame":
                    warnings.warn(f"{msg} In the meantime, PIL blur will be used instead.")
                    method = "pil"
            else:
                warnings.warn(f"{msg} In the meantime, parts of the program that "
                              f"should have been blurred will not be blurred.")
                method = None

        self.method = method
        super().__init__()

    def render_surface(self, element, surface: pygame.Surface, pos, size, alpha):
        if self.method is None:
            return

        cached = self._cache.get(element)
        if self.recalculate_each_tick or not cached or not cached or (pos, size) != cached[1]:

            if pos[1] + size[1] > surface.get_height():
                size = size[0], surface.get_height() - pos[1]
            new = surface.subsurface(pos, size)

            if self.method == "pil":
                img = Image.frombytes("RGBA", new.get_size(), pygame.image.tostring(new, "RGBA", False))
                img = img.filter(ImageFilter.GaussianBlur(radius=self.radius * alpha / 255))
                blurred_surface = pygame.image.frombuffer(img.tobytes(), img.size, "RGBA")

            else:
                blurred_surface = pygame.transform.gaussian_blur(new, int(self.radius * alpha / 255))

            self._cache[element] = (blurred_surface, (pos, size))

        else:
            blurred_surface = cached[0]

        surface.blit(blurred_surface, (0, 0))

    def draw_surface(self, element, destination_surface, pos):
        if element in self._cache:
            destination_surface.blit(self._cache[element][0], pos)
