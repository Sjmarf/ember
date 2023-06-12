import pygame
from typing import TYPE_CHECKING, Literal


from ember.ui.base.element import Element

if TYPE_CHECKING:
    pass

from .transition import Transition, TransitionController


class Slide(Transition):
    def __init__(
        self,
        duration: float = 0.2,
        direction: Literal["up", "down", "left", "right"] = "up",
        spacing: int = 5,
    ):
        super().__init__()
        self.duration = duration
        self.direction = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }[direction]
        self.spacing = spacing

    def _render_element(
        self,
        controller: TransitionController,
        timer: float,
        old: Element,
        new: Element,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ):
        progress = 1 - (timer / self.duration)

        alpha = int((1 - progress) * alpha)

        if old is not None:
            width, height = (
                old.rect.w + self.spacing,
                old.rect.h + self.spacing,
            )
            new_offset = (
                offset[0] + self.direction[0] * width * progress,
                offset[1] + self.direction[1] * height * progress,
            )
            old._render(surface, new_offset, alpha=alpha)

        if new is not None:
            width, height = (
                new.rect.w + self.spacing,
                new.rect.h + self.spacing,
            )
            new_offset = (
                offset[0] + self.direction[0] * width * (progress - 1),
                offset[1] + self.direction[1] * height * (progress - 1),
            )
            new._render(surface, new_offset, alpha=255 - alpha)
