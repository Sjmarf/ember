import pygame
from typing import Optional, TYPE_CHECKING

from ember.ui.base.element import Element
from .state import State

if TYPE_CHECKING:
    from ember.transition.transition import Transition

from ember import common as _c


class StateController:
    __slots__ = (
        "_previous_state",
        "_state",
        "element",
        "transition",
        "playing",
        "timer",
    )

    def __init__(self, element: Element):
        self._previous_state: Optional[State] = None
        self._state: Optional[State] = None
        self.element: Element = element

        self.transition: Optional["Transition"] = None

        self.playing: bool = False
        self.timer: float = 0.0

    def __repr__(self) -> str:
        return "<StateController>"

    def set_state(
        self, state: State, transition: Optional["Transition"] = None
    ) -> None:
        if self._state is not state:
            if self._state is not None:
                transition = (
                    transition
                    if transition is not None
                    else self.element._style.material_transition
                )
                if transition:
                    if (
                        self.transition is not None
                        and self.playing
                        and state == self._previous_state
                    ):
                        self.timer = transition.duration - (
                            self.timer / self.transition.duration * transition.duration
                        )
                    else:
                        self.timer = transition.duration
                    self.transition = transition
                    self.playing = True

            self._previous_state = self._state
            self._state = state

    def render(
        self,
        state: State,
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int = 255,
        transition: Optional["Transition"] = None,
    ) -> None:
        self.set_state(state, transition=transition)
        if self.playing:
            self.transition._render_material(
                self,
                self.timer,
                self.element,
                self._previous_state.material,
                self._state.material,
                surface,
                pos,
                size,
                alpha,
            )
            self.timer -= _c.delta_time
            if self.timer <= 0:
                self.playing = False

        elif self._state:
            self._state.material.render(self.element, surface, pos, size, alpha)
            self._state.material.draw(self.element, surface, pos)

    @property
    def element_offset(self) -> tuple[float, float]:
        if self.playing:
            offset = (
                self._previous_state.element_offset[0]
                + (
                    self._previous_state.element_offset[0]
                    - self._state.element_offset[0]
                )
                * 1
                - (self.timer / self.transition.duration),
                self._previous_state.element_offset[1]
                + (
                    self._previous_state.element_offset[1]
                    - self._state.element_offset[1]
                )
                * 1
                - (self.timer / self.transition.duration),
            )
            return offset
        else:
            return self._state.element_offset
