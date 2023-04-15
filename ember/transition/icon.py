import pygame
import os
from typing import Union, Optional, TYPE_CHECKING

from ember import common as _c
from ember.ui.element import Element

if TYPE_CHECKING:
    from ember.ui.view import View

from ember.transition.transition import Transition, ElementTransitionController


class IconMorph(Transition):
    def __init__(self, duration: float = 0.1):
        super().__init__()
        self.duration = duration
        self.direcion = 0
        self.frame_count = 0
        self.frame_height = 0
        
    def new_element_controller(self,
                               old_element: Optional["Transition"] = None,
                               new_element: Optional["Transition"] = None
                               ):
        controller = ElementTransitionController(self, old_element=old_element, new_element=new_element)
        self._load_sheet(controller, old_element.icon, new_element.icon)
        return controller
        
    def _load_sheet(self, controller: ElementTransitionController, from_name, to_name):
        try:
            path = str(_c.package.joinpath(f'{controller.old_element.style.font.name}/icon_animations/{from_name}${to_name}.png'))
            controller.sheet = pygame.image.load(path).convert_alpha()
            controller.direction = 1
        except FileNotFoundError:
            try:
                path = str(_c.package.joinpath(f'{controller.old_element.style.font.name}/icon_animations/{to_name}${from_name}.png'))
                controller.sheet = pygame.image.load(path).convert_alpha()
                controller.direction = -1
            except FileNotFoundError:
                raise ValueError(f"The icons '{from_name}' and '{to_name}' don't have a transition"
                                 f" animation.")

        controller.sheet.fill(controller.old_element.col, special_flags=pygame.BLEND_RGB_ADD)
        controller.frame_height = controller.old_element.get_surface().get_height()
        controller.frame_count = controller.sheet.get_height()/controller.frame_height

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
        
        frame = int((timer/self.duration)*controller.frame_count)
        if controller.direction == 1:
            frame = controller.frame_count - frame - 1
        frame_surf = controller.sheet.subsurface((0, frame * controller.frame_height, controller.sheet.get_abs_width(), controller.frame_height))
        new_element.draw_surface(surface, offset, frame_surf)
