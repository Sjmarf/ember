import pygame

from typing import Optional, TYPE_CHECKING

from .. import common as _c
from ..material.material import Material
from ..event import TRANSITIONSTARTED

from ..state.state_controller import StateController

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class Transition:
    """
    All transitions inherit from this class. This base class should not be instantiated.
    """

    def __init__(self, duration: float) -> None:
        self.duration: float = duration
        """
        The duration of the transition in seconds.
        """

    def _new_element_controller(
        self,
        old_element: Optional["Element"] = None,
        new_element: Optional["Element"] = None,
    ) -> "TransitionController":
        return TransitionController(
            self, old_element=old_element, new_element=new_element
        )

    @staticmethod
    def _update_element(controller: "TransitionController") -> None:
        if controller.old_element is not None:
            controller.old_element._update()
        if controller.new_element is not None:
            controller.new_element._update()

    def _render_element(
        self,
        controller: "TransitionController",
        timer: float,
        old_element: Optional["Element"],
        new_element: Optional["Element"],
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        pass

    def _render_material(
        self,
        controller: "StateController",
        timer: float,
        element: "Element",
        old_material: Optional[Material],
        new_material: Optional[Material],
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        pass


class TransitionController:
    def __init__(
        self,
        *transitions: Transition,
        old_element: Optional["Element"] = None,
        new_element: Optional["Element"] = None,
    ) -> None:
        if len(transitions) == 1:
            self.transition_1 = transitions[0]
            self.transition_2 = None
        elif len(transitions) == 2:
            self.transition_1, self.transition_2 = transitions
        else:
            raise ValueError(
                f"You must provide either 1 or 2 transitions, not {len(transitions)}."
            )

        self.timer = self.transition_1.duration
        self.playing = False

        self.old_element = old_element
        self.new_element = new_element

        new_event = pygame.event.Event(TRANSITIONSTARTED, element=self.new_element)
        pygame.event.post(new_event)

    def update(self) -> None:
        self.playing = True
        self.transition_1._update_element(self)
        if self.transition_2 is not None:
            self.transition_2._update_element(self)

        self.timer -= _c.delta_time

    def _get_progress(self) -> float:
        val = pygame.math.clamp(self.timer / self.transition_1.duration, 0, 1)
        if self.old_element is not None:
            return val
        else:
            return 1 - val

    def render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        if self.transition_2 is not None:
            self.transition_1._render_element(
                self, self.timer, self.old_element, None, surface, offset, alpha
            )
            self.transition_1._render_element(
                self, self.timer, None, self.new_element, surface, offset, alpha
            )
        else:
            self.transition_1._render_element(
                self,
                self.timer,
                self.old_element,
                self.new_element,
                surface,
                offset,
                alpha,
            )

    progress: float = property(fget=_get_progress)
