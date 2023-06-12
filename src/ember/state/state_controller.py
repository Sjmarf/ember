import pygame
from typing import Optional, TYPE_CHECKING, Sequence

from ember.ui.base.element import Element

if TYPE_CHECKING:
    from .state import State
    from .material_state import MaterialState
    from ember.transition.transition import Transition

from .. import common as _c
from .. import log


class MaterialController:
    def __init__(self) -> None:
        self.transition: Optional["Transition"] = None
        self.playing: bool = False
        self.timer: float = 0.0

class StateController:
    __slots__ = ("previous_state", "current_state", "element", "material_controllers")

    def __init__(self, element: Element, materials: int = 1) -> None:
        self.previous_state: Optional["State"] = None
        self.current_state: Optional["State"] = None
        self.element: Element = element
        self.material_controllers: [MaterialController] = [
            MaterialController() for _ in range(materials)
        ]

        # self.transition: Optional["Transition"] = None

        # self.playing: bool = False
        # self.timer: float = 0.0

    def __getitem__(self, item: int) -> MaterialController:
        return self.material_controllers[item]

    def __repr__(self) -> str:
        return "<StateController>"

    def set_state(self, state: "State", transitions: Sequence["Transition"] = None) -> None:
        if self.current_state is not state:
            log.material.info(state, self.element, "Set state")
            if self.current_state is not None:
                if transitions:
                    for material_controller, transition in zip(
                        self.material_controllers, transitions
                    ):
                        if transition is None:
                            continue
                        if (
                            material_controller.transition is not None
                            and material_controller.playing
                            and state == self.previous_state
                        ):
                            material_controller.timer = transition.duration - (
                                material_controller.timer
                                / material_controller.transition.duration
                                * transition.duration
                            )
                        else:
                            material_controller.timer = transition.duration
                        material_controller.transition = transition
                        material_controller.playing = True

            self.previous_state = self.current_state
            self.current_state = state

    def render(
        self,
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int = 255,
        material_index=0,
    ) -> None:
        self.previous_state: "MaterialState"
        self.current_state: "MaterialState"

        material_controller = self.material_controllers[material_index]
        if material_controller.playing:
            material_controller.transition._render_material(
                self,
                material_controller.timer,
                self.element,
                self.previous_state.get_material(material_index),
                self.current_state.get_material(material_index),
                surface,
                pos,
                size,
                alpha,
            )
            material_controller.timer -= _c.delta_time
            if material_controller.timer <= 0:
                material_controller.playing = False

        elif self.current_state:
            self.current_state.get_material(material_index).render(
                self.element, surface, pos, size, alpha
            )
            self.current_state.get_material(material_index).draw(
                self.element, surface, pos
            )
