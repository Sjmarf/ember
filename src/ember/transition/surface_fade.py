import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.ui.base.element import Element
    from ..ui.surface import Surface

from .transition import Transition, TransitionController
from ..state.state_controller import StateController
from ..material.material import Material
from ..ui.base.surfacable import Surfacable

class SurfaceFade(Transition):
    """
    Transitions by blending the Surfaces mathmatically. This is less performant than
    :py:class:`ember.transition.Fade`, but looks nicer. Only works with Elements that inherit
    from :py:class:`ember.ui.Surfacable`.
    """
    def __init__(self, duration: float = 0.2) -> None:
        super().__init__(duration)

    def _new_element_controller(
        self,
        old_element: Optional[Surfacable] = None,
        new_element: Optional[Surfacable] = None,
    ) -> "TransitionController":
        if not (isinstance(old_element, Surfacable) and isinstance(new_element, Surfacable)):
            raise ValueError("Cannot use SurfaceFade on non-Surfacable elements.")
        return TransitionController(
            self, old=old_element, new=new_element
        )

    def _render_element(self,
                        controller: TransitionController,
                        timer: float,
                        old: Surfacable,
                        new: Surfacable,
                        surface: pygame.Surface,
                        offset: tuple[int, int],
                        alpha: int = 255
                        ) -> None:
        amount = max(0.0, timer / self.duration)

        old_surf = old._get_surface()
        new_surf = new._get_surface()

        result = surface_fade(old_surf, new_surf, amount)
        new._draw_surface(surface, offset, result)

    def _render_material(self,
                         controller: "StateController",
                         timer: float,
                         element: "Element",
                         old: Optional[Material],
                         new: Optional[Material],
                         surface: pygame.Surface,
                         pos: tuple[int, int],
                         size: tuple[int, int],
                         alpha: int = 255) -> None:

        if old is not None and new is not None:
            amount = max(0.0, timer / self.duration)
            old_surf = old.render(element, surface, pos, size, alpha)
            new_surf = new.render(element, surface, pos, size, alpha)
            if (old_surf is None) and (new_surf is None):
                return
            result = surface_fade(old_surf, new_surf, amount)
            surface.blit(result, pos)

        else:
            if old is not None:
                new_alpha = round(timer / self.duration * alpha)
                old.draw(element, surface, pos, size, new_alpha)

            else:
                new_alpha = round((1 - timer / self.duration) * alpha)
                new.draw(element, surface, pos, size, new_alpha)


def surface_fade(old_surf: pygame.Surface, new_surf: pygame.Surface, amount: float) -> pygame.Surface:
    if old_surf is None:
        new_surf.set_alpha(255*(1-amount))
        return new_surf
    elif new_surf is None:
        old_surf.set_alpha(255*amount)
        return old_surf

    if old_surf.get_size() != new_surf.get_size():
        largest_width = max(old_surf.get_width(), new_surf.get_width())
        largest_height = max(old_surf.get_height(), new_surf.get_height())

        surf1 = pygame.Surface((largest_width, largest_height), pygame.SRCALPHA)
        surf2 = pygame.Surface((largest_width, largest_height), pygame.SRCALPHA)

        surf1.blit(old_surf, (largest_width / 2 - old_surf.get_width() / 2,
                              largest_height / 2 - old_surf.get_height() / 2))
        surf2.blit(new_surf, (largest_width / 2 - new_surf.get_width() / 2,
                              largest_height / 2 - new_surf.get_height() / 2))
    else:
        surf1, surf2 = old_surf, new_surf
        del old_surf, new_surf

    result = surf1.copy()
    old_px = pygame.surfarray.pixels3d(result)
    new_px = pygame.surfarray.pixels3d(surf2)
    old_a = pygame.surfarray.pixels_alpha(result)
    new_a = pygame.surfarray.pixels_alpha(surf2)

    for i in range(3):
        old_px[:, :, i] = (new_px[:, :, i] * (1 - amount) + old_px[:, :, i] * amount)

    old_a[:] = (new_a[:] * (1 - amount) + old_a[:] * amount)
    del old_px, old_a

    return result
