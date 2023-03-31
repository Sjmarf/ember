import pygame

from typing import Optional, TYPE_CHECKING

from ember import common as _c
from ember.ui.element import Element
from ember.material.material import Material

if TYPE_CHECKING:
    from ember.ui.view import View


class ElementTransitionType:
    def new_element_controller(self,
                               old_element: Optional[Element] = None,
                               new_element: Optional[Element] = None
                               ):
        pass


class MaterialTransitionType:
    def new_material_controller(self,
                                old_material: Optional[Material] = None,
                                new_material: Optional[Material] = None):
        pass


class Transition(ElementTransitionType, MaterialTransitionType):
    def __init__(self):
        self.duration = 0

    def new_element_controller(self,
                               old_element: Optional[Element] = None,
                               new_element: Optional[Element] = None
                               ):
        return ElementTransitionController(self, old_element=old_element, new_element=new_element)

    def new_material_controller(self,
                                old_material: Optional[Material] = None,
                                new_material: Optional[Material] = None):
        return MaterialTransitionController(self, old_material=old_material, new_material=new_material)

    @staticmethod
    def update_element(controller: "ElementTransitionController", root: "View"):
        if controller.old_element is not None:
            controller.old_element.update(root)
        if controller.new_element is not None:
            controller.new_element.update(root)

    def render_element(self,
                       controller: "ElementTransitionController",
                       timer: float,
                       old_element: Optional[Element],
                       new_element: Optional[Element],
                       surface: pygame.Surface,
                       offset: tuple[int, int],
                       root: "View",
                       alpha: int = 255):
        pass

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
        pass


class MaterialTransitionController(MaterialTransitionType):
    def __init__(self,
                 *transitions: Transition,
                 old_material: Optional[Material] = None,
                 new_material: Optional[Material] = None
                 ):
        if len(transitions) == 1:
            self.transition_1 = transitions[0]
            self.transition_2 = None
        elif len(transitions) == 2:
            self.transition_1, self.transition_2 = transitions
        else:
            raise ValueError(f"You must provide either 1 or 2 transitions, not {len(transitions)}.")

        self.timer = self.transition_1.duration
        self.playing = False

        self.old_material = old_material
        self.new_material = new_material

    def new_material_controller(self, **kwargs):
        return self

    def render(self,
               element: Element,
               surface: pygame.Surface,
               pos: tuple[int,int],
               size: tuple[int,int],
               alpha: int):
        self.playing = True
        self.timer -= _c.delta_time

        if self.transition_2 is not None:
            self.transition_1.render_material(self, self.timer, element, self.old_material, None,
                                              surface, pos, size, alpha)
            self.transition_1.render_material(self, self.timer, element, None, self.new_material,
                                              surface, pos, size, alpha)
        else:
            self.transition_1.render_material(self, self.timer, element, self.old_material, self.new_material,
                                              surface, pos, size, alpha)


class ElementTransitionController(ElementTransitionType):
    def __init__(self,
                 *transitions: Transition,
                 old_element: Optional[Element] = None,
                 new_element: Optional[Element] = None
                 ):
        if len(transitions) == 1:
            self.transition_1 = transitions[0]
            self.transition_2 = None
        elif len(transitions) == 2:
            self.transition_1, self.transition_2 = transitions
        else:
            raise ValueError(f"You must provide either 1 or 2 transitions, not {len(transitions)}.")

        self.timer = self.transition_1.duration
        self.playing = False

        self.old_element = old_element
        self.new_element = new_element

    def new_element_controller(self, **kwargs):
        return self

    def update(self, root: "View"):
        self.playing = True
        self.transition_1.update_element(self, root)
        if self.transition_2 is not None:
            self.transition_2.update_element(self, root)

        self.timer -= _c.delta_time

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View", alpha: int = 255):
        if self.transition_2 is not None:
            self.transition_1.render_element(self, self.timer, self.old_element, None,
                                             surface, offset, root, alpha)
            self.transition_1.render_element(self, self.timer, None, self.new_element,
                                             surface, offset, root, alpha)
        else:
            self.transition_1.render_element(self, self.timer, self.old_element, self.new_element,
                                             surface, offset, root, alpha)
