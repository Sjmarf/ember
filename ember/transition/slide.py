import pygame
from typing import Union, Literal, Callable, TYPE_CHECKING

from ember import common as _c
from ember.ui.element import Element

if TYPE_CHECKING:
    from ember.ui.view import View

from ember.transition.transition import Transition, ElementTransitionController


class Slide(Transition):
    def __init__(self,
                 duration: float = 0.2, direction: Literal["up", "down", "left", "right"] = "up",
                 spacing: int = 5):
        super().__init__()
        self.duration = duration
        self.direction = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]
        self.spacing = spacing

    def render_element(self,
                       controller: ElementTransitionController,
                       timer: float,
                       old_element: Element,
                       new_element: Element,
                       surface: pygame.Surface,
                       offset: tuple[int, int],
                       root: "View",
                       alpha: int = 255
                       ):
        progress = 1 - (timer / self.duration)

        alpha = int((1 - progress) * alpha)

        if old_element is not None:
            width, height = old_element.rect.w + self.spacing, old_element.rect.h + self.spacing
            new_offset = (offset[0] + self.direction[0] * width * progress,
                          offset[1] + self.direction[1] * height * progress)
            old_element._render(surface, new_offset, root, alpha=alpha)

        if new_element is not None:
            width, height = new_element.rect.w + self.spacing, new_element.rect.h + self.spacing
            new_offset = (offset[0] + self.direction[0] * width * (progress - 1),
                          offset[1] + self.direction[1] * height * (progress - 1))
            new_element._render(surface, new_offset, root, alpha=255 - alpha)
