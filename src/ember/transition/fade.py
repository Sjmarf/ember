import pygame
from typing import Optional, TYPE_CHECKING

from ..ui.element import Element

if TYPE_CHECKING:
    from ..ui.view import View

from .transition import Transition, ElementTransitionController, MaterialTransitionController
from ..material.material import Material


class Fade(Transition):
    def __init__(self, duration: float = 0.2):
        super().__init__()
        self.duration = duration

    def render_element(self,
                       controller: ElementTransitionController,
                       timer: float,
                       old_element: Element,
                       new_element: Element,
                       surface: pygame.Surface,
                       offset: tuple[int, int],
                       root: "View",
                       alpha: int = 255):

        alpha = int(timer / self.duration * alpha)
        if old_element is not None:
            old_element._render(surface, offset, root, alpha=alpha)
        if new_element is not None:
            new_element._render(surface, offset, root, alpha=(255 - alpha))

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

        if old_material is not None:
            new_alpha = int(timer / self.duration * alpha)
            old_material.render_surface(element, size, new_alpha)
            old_material.draw_surface(element, surface, pos)

        if new_material is not None:
            new_alpha = int((1 - timer / self.duration) * alpha)
            new_material.render_surface(element, size, new_alpha)
            new_material.draw_surface(element, surface, pos)
