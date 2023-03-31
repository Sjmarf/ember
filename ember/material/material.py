import pygame
from weakref import WeakKeyDictionary

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.transition.transition import MaterialTransitionController, Transition


class Material:
    def __init__(self):
        self._cache = WeakKeyDictionary()

    def render_surface(self, element, surface: pygame.Surface, pos, size, alpha):
        pass

    def get_surface(self, element):
        return self._cache.get(element)

    def draw_surface(self, element, destination_surface, pos):
        if element in self._cache:
            destination_surface.blit(self._cache[element], pos)


class MaterialController:
    def __init__(self, element):
        self._material: Optional[Material] = None
        self.element = element
        self.controller: Optional["MaterialTransitionController"] = None

    def set_material(self, material, transition: Optional["Transition"] = None):
        if self._material is not material:
            if self._material is not None:
                if transition:
                    self.controller = transition.new_material_controller(self._material, material)
                elif hasattr(self.element, "style") and \
                        hasattr(self.element.style, "material_transition") and \
                        self.element.style.material_transition:
                    self.controller = self.element.style.material_transition.new_material_controller(self._material,
                                                                                                     material)
            self._material = material

    def render(self, element, surface, pos, size, alpha):
        if self.controller:
            self.controller.render(element, surface, pos, size, alpha)
            if self.controller.timer <= 0:
                self.controller = None

        elif self._material:
            self._material.render_surface(element, surface, pos, size, alpha)
            self._material.draw_surface(element, surface, pos)
