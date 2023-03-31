import pygame
from typing import Optional

from ember import common as _c
from ember.ui.view import View
from ember.ui.element import Element
from ember.ui.surface import Surface

from ember.transition.transition import Transition, ElementTransitionController, MaterialTransitionController
from ember.material.material import Material

class SurfaceFade(Transition):
    def __init__(self, duration: float = 0.2):
        super().__init__()
        self.duration = duration

    def render_element(self,
                       controller: ElementTransitionController,
                       timer: float,
                       old_element: Surface,
                       new_element: Surface,
                       surface: pygame.Surface,
                       offset: tuple[int, int],
                       root: View,
                       alpha: int = 255
                       ):
        amount = timer / self.duration

        old_surf = old_element.get_surface()
        new_surf = new_element.get_surface()

        result = surface_fade(old_surf, new_surf, amount)
        new_element.draw_surface(surface, offset, result)

    def render_material(self,
                        controller: "MaterialTransitionController",
                        timer: float,
                        element: Element,
                        old_material: Optional[Material],
                        new_material: Optional[Material],
                        surface: pygame.Surface,
                        pos: tuple[int, int],
                        size: tuple[int, int],
                        alpha: int = 255):

        if old_material and new_material:
            amount = max(0, timer / self.duration)
            old_material.render_surface(element, surface, pos, size, alpha)
            old_surf = old_material.get_surface(element)
            new_material.render_surface(element, surface, pos, size, alpha)
            new_surf = new_material.get_surface(element)

            result = surface_fade(old_surf, new_surf, amount)
            surface.blit(result, pos)

        else:
            if old_material is not None:
                new_alpha = round(timer / self.duration * alpha)
                old_material.render_surface(element, surface, pos, size, new_alpha)
                old_material.draw_surface(element, surface, pos)

            else:
                new_alpha = round((1 - timer / self.duration) * alpha)
                new_material.render_surface(element, surface, pos, size, new_alpha)
                new_material.draw_surface(element, surface, pos)


def surface_fade(old_surf, new_surf, amount):
    if old_surf.get_size() != new_surf.get_size():
        largest_width = max(old_surf.get_width(), new_surf.get_width())
        largest_height = max(old_surf.get_height(), new_surf.get_height())

        surf1 = pygame.Surface((largest_width, largest_height), pygame.SRCALPHA)
        surf2 = pygame.Surface((largest_width, largest_height), pygame.SRCALPHA)

        surf1.blit(old_surf, (largest_width / 2 - surf1.get_width() / 2,
                              largest_height / 2 - surf2.get_height() / 2))
        surf2.blit(new_surf, (largest_width / 2 - surf1.get_width() / 2,
                              largest_height / 2 - surf2.get_height() / 2))
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
