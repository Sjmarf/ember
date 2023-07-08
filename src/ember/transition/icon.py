import pygame
from typing import Optional, TYPE_CHECKING

from .. import common as _c
from ember.ui.base.element import Element

if TYPE_CHECKING:
    pass

from .transition import Transition, TransitionController


class IconMorph(Transition):
    def __init__(self, duration: float = 0.1):
        super().__init__()
        self.duration = duration
        self.direcion = 0
        self.frame_count = 0
        self.frame_height = 0
        
    def _new_element_controller(self,
                                old_element: Optional["Transition"] = None,
                                new_element: Optional["Transition"] = None
                                ):
        controller = TransitionController(self, old=old_element, new=new_element)
        self._load_sheet(controller, old_element.icon, new_element.icon)
        return controller
        
    def _load_sheet(self, controller: TransitionController, from_name, to_name):
        try:
            path = str(_c.package.joinpath(f'{controller.old.style.font.name}/icon_animations/{from_name}${to_name}.png'))
            controller.sheet = pygame.image.load(path).convert_alpha()
            controller.direction = 1
        except FileNotFoundError:
            try:
                path = str(_c.package.joinpath(f'{controller.old.style.font.name}/icon_animations/{to_name}${from_name}.png'))
                controller.sheet = pygame.image.load(path).convert_alpha()
                controller.direction = -1
            except FileNotFoundError:
                raise ValueError(f"The icons '{from_name}' and '{to_name}' don't have a transition"
                                 f" animation.")

        controller.sheet.fill(controller.old.col, special_flags=pygame.BLEND_RGB_ADD)
        controller.frame_height = controller.old.get_surface().get_h()
        controller.frame_count = controller.sheet.get_height()/controller.frame_height

    def _render_element(self,
                        controller: TransitionController,
                        timer: float,
                        old: Element,
                        new: Element,
                        surface: pygame.Surface,
                        offset: tuple[int, int],
                        alpha: int = 255
                        ):
        
        frame = int((timer/self.duration)*controller.frame_count)
        if controller.direction == 1:
            frame = controller.frame_count - frame - 1
        frame_surf = controller.sheet.subsurface((0, frame * controller.frame_height, controller.sheet.get_abs_w(), controller.frame_height))
        new.draw_surface(surface, offset, frame_surf)
