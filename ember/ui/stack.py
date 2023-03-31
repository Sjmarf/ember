import pygame
from typing import Optional

from ember import common as _c
from ember.ui.element import Element
from ember.ui.view import View
from ember.size import Size, FIT, FILL
from ember.transition.transition import Transition

from ember.material.material import MaterialController


class Layout(Element):
    def __init__(self, width, height):
        self._first_visible_element = None
        self.material_controller = MaterialController(self)
        self.material_controller.set_material(self.background)
        super().__init__(width, height)

    def _calculate_size(self, elements, size, width, height):
        self._fit_width = 0
        self._fit_height = 0

        if size is None and width is None:
            width = FILL if any(i.width.mode == 2 for i in elements) else FIT
        if size is None and height is None:
            height = FILL if any(i.height.mode == 2 for i in elements) else FIT

        width = size[0] if width is None else width
        height = size[1] if height is None else height
        return width, height

    def __getitem__(self, item):
        if type(item) is int:
            return self._elements[item]
        else:
            return NotImplemented

    def __len__(self):
        return len(self._elements)

    def __contains__(self, item):
        return item in self._elements

    def set_elements(self, *elements, animation: Optional[Transition] = None):
        old_elements = self._elements.copy() if animation else None
        if self.root is not None:
            if self.root.element_focused in self._elements and self.root.element_focused not in elements:
                self.root.element_focused = None

        self._elements = list(elements)
        self._update_elements(animation=animation, old_elements=old_elements)

    def append(self, element, animation: Optional[Transition] = None):
        old_elements = self._elements.copy() if animation else None
        self._elements.append(element)
        self._update_elements(animation=animation, old_elements=old_elements)

    def insert(self, index, element, animation: Optional[Transition] = None):
        old_elements = self._elements.copy() if animation else None
        self._elements.insert(index, element)
        self._update_elements(animation=animation, old_elements=old_elements)

    def remove(self, element, animation: Optional[Transition] = None):
        old_elements = self._elements.copy() if animation else None

        if type(element) is int:
            element = self._elements[element]
        self._elements.remove(element)

        if self.root is not None:
            if self.root.element_focused is element:
                self.root.element_focused = None
        self._update_elements(animation=animation, old_elements=old_elements)

    def set_root(self, root):
        self.root = root
        [i.set_root(root) for i in self._elements]

    def _get_elements(self):
        return self._elements

    def _update_elements(self, animation: Optional[Transition] = None, old_elements=None):
        if animation:
            self.animation = animation.new_element_controller()
            self.animation.old_element = type(self)(*old_elements)
            self.animation.new_element = self

        [i.set_parent(self) for i in self._elements]
        self.calc_fit_size()

    def index(self, element):
        return self._elements.index(element)

    def update(self, root: View):
        for i in self._elements[self._first_visible_element:]:
            i.update_a(root)
            if not i.visible:
                break

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):
        rect = self.rect.move(*offset)
        if self.background:
            self.material_controller.render(self, surface, (
                    rect.x - surface.get_abs_offset()[0],
                    rect.y - surface.get_abs_offset()[1]),
                                           rect.size, alpha)

        for i in self._elements[self._first_visible_element:]:
            i.render_a(surface, offset, root, alpha=alpha)
            if not i.visible:
                break

    def event(self, event, root: View):
        for i in self._elements[self._first_visible_element:]:
            i.event(event,root)
            if not i.visible:
                break

    def calc_fit_size(self):
        pass

    elements = property(
        fget=_get_elements
    )

