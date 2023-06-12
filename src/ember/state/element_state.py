from copy import copy
from ember.material import Material
from typing import Sequence, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .state_controller import StateController, MaterialController

from .material_state import SingleMaterialState

class ElementState(SingleMaterialState):
    def __init__(
        self,
        material: Optional[Material] = None,
        element_offset: Sequence[int] = (0, 0),
        element_alpha: int = 255,
    ):
        self.element_offset: Sequence[int] = element_offset
        self.element_alpha: int = element_alpha
        super().__init__(material=material)

    @staticmethod
    def get_element_offset(state_controller: "StateController", material_index: int = 0) -> tuple[int, int]:
        material_controller = state_controller.material_controllers[material_index]
        if material_controller.playing:
            offset = (
                state_controller.previous_state.element_offset[0]
                + (
                    state_controller.previous_state.element_offset[0]
                    - state_controller.current_state.element_offset[0]
                )
                * 1
                - (material_controller.timer / material_controller.transition.duration),
                state_controller.previous_state.element_offset[1]
                + (
                    state_controller.previous_state.element_offset[1]
                    - state_controller.current_state.element_offset[1]
                )
                * 1
                - (material_controller.timer / material_controller.transition.duration),
            )
            return offset
        else:
            return state_controller.current_state.element_offset
