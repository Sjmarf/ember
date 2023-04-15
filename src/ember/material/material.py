import pygame
from weakref import WeakKeyDictionary

from typing import Optional, TYPE_CHECKING
from .. import log

if TYPE_CHECKING:
    from ..transition.transition import MaterialTransitionController, Transition


class Material:
    def __init__(self):
        self._cache = WeakKeyDictionary()

    def render_surface(self, element, surface: pygame.Surface, pos, size, alpha):
        pass

    def get_surface(self, element):
        return self._cache.get(element)

    def draw_surface(self, element, destination_surface, pos, alpha):
        if element in self._cache:
            self._cache[element].set_alpha(alpha)
            destination_surface.blit(self._cache[element], pos)


class MaterialController:
    def __init__(self, element):
        self._material: Optional[Material] = None
        self.element = element
        self.controller: Optional["MaterialTransitionController"] = None

    def __repr__(self):
        return "<MaterialController>"

    def set_material(self, material, transition: Optional["Transition"] = None):
        if self._material is not material:
            log.material.info(self, self.element, f"Changed material to {material}")
            if self._material is not None:
                if transition:
                    self.controller = transition.new_material_controller(self._material, material)

            self._material = material

    def render(self, element, surface, pos, size, alpha):
        if self.controller:
            self.controller.render(element, surface, pos, size, alpha)
            if self.controller.timer <= 0:
                self.controller = None

        elif self._material:
            self._material.render_surface(element, surface, pos, size, alpha)
            self._material.draw_surface(element, surface, pos, alpha)
