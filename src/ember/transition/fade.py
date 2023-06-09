import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.ui.base.element import Element

from .transition import Transition
from ..state.state_controller import StateController
from ..material.material import Material


class Fade(Transition):
    """
    Transitions by decreasing the alpha of the first surface and increasing the alpha of the second surface.
    """
    def __init__(self, duration: float = 0.2):
        super().__init__(duration)

    def _render_element(self,
                        controller: StateController,
                        timer: float,
                        old: "Element",
                        new: "Element",
                        surface: pygame.Surface,
                        offset: tuple[int, int],
                        alpha: int = 255):

        alpha = int(timer / self.duration * alpha)
        if old is not None:
            old._render(surface, offset, alpha=alpha)
        if new is not None:
            new._render(surface, offset, alpha=(255 - alpha))

    def _render_material(self,
                         controller: "StateController",
                         timer: float,
                         element: "Element",
                         old: Optional[Material],
                         new: Optional[Material],
                         surface: pygame.Surface,
                         pos: tuple[int, int],
                         size: tuple[int, int],
                         alpha: int = 255):

        if old is not None:
            new_alpha = int(timer / self.duration * alpha)
            old.draw(element, surface, pos, size, new_alpha)

        if new is not None:
            new_alpha = int((1 - timer / self.duration) * alpha)
            new.draw(element, surface, pos, size, new_alpha)
