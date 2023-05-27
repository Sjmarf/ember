import pygame
import warnings
from .material import Material
from typing import Optional, Literal, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.ui.base.element import Element

from .. import common as _c

try:
    from PIL import Image, ImageFilter

    pillow_installed = True
except ModuleNotFoundError:
    pillow_installed = False


class Blur(Material):
    def __init__(
        self,
        radius: int = 7,
        method: Optional[Literal["pil", "pygame"]] = "pygame",
        recalculate_each_tick: bool = False,
        alpha: int = 255,
    ):
        self.radius = radius
        self.recalculate_each_tick = recalculate_each_tick

        ver = pygame.version.vernum
        if not _c.is_ce:
            msg = (
                "You are using the upstream version of Pygame, which does not support blurring. "
                "\n\nTo fix this, install pygame-ce by running 'pip uninstall pygame' followed by "
                "'pip install pygame-ce'."
            )
            if pillow_installed:
                if method == "pygame":
                    warnings.warn(
                        f"{msg} In the meantime, PIL blur will be used instead."
                    )
                    method = "pil"
            else:
                warnings.warn(
                    f"{msg} In the meantime, parts of the program that "
                    f"should have been blurred will not be blurred."
                )
                method = None

        elif ver < (2, 2):
            msg = (
                "You are using an outdated version of pygame-ce, which does not support blurring. "
                "\n\nTo fix this, "
                "upgrade pygame-ce to version 2.2.0 or later using 'pip install pygame-ce --upgrade'."
            )

            if pillow_installed:
                if method == "pygame":
                    warnings.warn(
                        f"{msg} In the meantime, PIL blur will be used instead."
                    )
                    method = "pil"
            else:
                warnings.warn(
                    f"{msg} In the meantime, parts of the program that "
                    f"should have been blurred will not be blurred."
                )
                method = None

        self.method = method
        super().__init__(alpha)

    def __repr__(self) -> str:
        return f"<Blur({self.radius})>"

    def _needs_to_render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> bool:
        if self.method is None:
            return False

        return (
            self.recalculate_each_tick
            or element not in self._cache
            or (pos, size) != self._cache[element][1]
        )

    def _render_surface(
        self,
        element: Optional["Element"],
        surface: Optional[pygame.Surface],
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> Any:

        if pos[1] + size[1] > surface.get_height():
            size = size[0], surface.get_height() - pos[1]
        new = surface.subsurface(pos, size)

        if self.method == "pil":
            img = Image.frombytes(
                "RGBA", new.get_size(), pygame.image.tostring(new, "RGBA", False)
            )
            img = img.filter(ImageFilter.GaussianBlur(radius=self.radius))
            blurred_surface = pygame.image.frombuffer(
                img.tobytes(), img.size, "RGBA"
            )

        else:
            blurred_surface = pygame.transform.gaussian_blur(new, int(self.radius))

        return (blurred_surface, (pos, size))

    def _get(self, element: "Element") -> Optional[pygame.Surface]:
        return self._cache[element][0]
