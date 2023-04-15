import pygame
from typing import Optional, NoReturn, Sequence

from .. import common as _c
from .. import log
from .element import Element
from .view import View
from ..size import SizeType
from ..transition.transition import Transition

from ..material.material import MaterialController

from ..style.stack_style import StackStyle
from ..style.load_style import load as load_style


class Stack(Element):
    def __init__(self,
                 size: Sequence[SizeType],
                 width: SizeType,
                 height: SizeType,
                 default_size: Sequence[SizeType] = (20, 20)
                 ):

        """
        The base class for VStack and HStack.

        :param size:
        :param width:
        :param height:
        :param default_size:
        """

        self._first_visible_element: Optional[Element] = None

        self.material_controller: MaterialController = MaterialController(self)
        """
        The :ref:`MaterialController<material-controller>` object responsible for managing the Stack's 
        background materials.
        """

        super().__init__(size, width, height, default_size=default_size)

    def __getitem__(self, item: int) -> Element:
        if isinstance(item, int):
            return self._elements[item]
        else:
            return NotImplemented

    def __setitem__(self, key: int, value: Element) -> NoReturn:
        if not isinstance(key, int) or not isinstance(value, Element):
            return NotImplemented

        self._elements[key] = value
        value._set_parent(self)
        self._update_rect_chain_up()

    def __len__(self) -> int:
        return len(self._elements)

    def __contains__(self, item: Element) -> bool:
        return item in self._elements

    def _load_element(self, element: Element) -> Element:
        """
        Used internally by the library.
        """
        # Called inside of set_elements, append, etc. This exists because the list base class overrides it
        element._set_parent(self)
        return element

    def set_elements(self, *elements: Element, animation: Optional[Transition] = None,
                     _supress_update: bool = False) -> NoReturn:
        """
        Replace the elements in the stack with new elements.
        """

        if elements and isinstance(elements[0], list):
            elements = elements[0]
        old_elements = self._elements.copy() if animation else None
        if self.root is not None:
            if self.root.element_focused in self._elements and self.root.element_focused not in elements:
                self.root.element_focused = None

        self._elements.clear()
        for i in elements:
            self._elements.append(self._load_element(i))
        if not _supress_update:
            self._update_elements(animation=animation, old_elements=old_elements)

    def append(self, element: Element, animation: Optional[Transition] = None) -> NoReturn:
        """
        Append an element to the end of the stack.
        """
        old_elements = self._elements.copy() if animation else None
        self._elements.append(self._load_element(element))
        self._update_elements(animation=animation, old_elements=old_elements)

    def insert(self, index: int, element: Element, animation: Optional[Transition] = None) -> NoReturn:
        """
        Insert an element before at an index.
        """
        old_elements = self._elements.copy() if animation else None
        self._elements.insert(index, self._load_element(element))
        self._update_elements(animation=animation, old_elements=old_elements)

    def pop(self, index: int = -1, animation: Optional[Transition] = None) -> Element:
        """
        Remove and return an element at an index (default last).
        """
        old_elements = self._elements.copy() if animation else None
        element = self._elements.pop(index)

        if self.root is not None:
            if self.root.element_focused is element:
                self.root.element_focused = None
        self._update_elements(animation=animation, old_elements=old_elements)
        return element

    def remove(self, element: Element, animation: Optional[Transition] = None) -> NoReturn:
        """
        Remove an element from the stack.
        """
        old_elements = self._elements.copy() if animation else None
        self._elements.remove(element)

        if self.root is not None:
            if self.root.element_focused is element:
                self.root.element_focused = None
        self._update_elements(animation=animation, old_elements=old_elements)

    def _set_root(self, root: View) -> NoReturn:
        self.root = root
        [i._set_root(root) for i in self._elements]

    def _update_elements(self, animation: Optional[Transition] = None,
                         old_elements: Sequence[Element] = None) -> NoReturn:
        if animation:
            self.animation = animation.new_element_controller()
            self.animation.old_element = type(self)(*old_elements)
            self.animation.new_element = self

        self._update_rect_chain_up()

    def index(self, element: Element) -> int:
        """
        Returns the index of the element.
        """
        return self._elements.index(element)

    def _update(self, root: View) -> NoReturn:
        for i in self._elements[self._first_visible_element:]:
            i._update_a(root)
            if not i.is_visible:
                break

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: View,
                alpha: int = 255) -> NoReturn:
        self._render_background(surface, offset, root, alpha)
        self._render_elements(surface, offset, root, alpha)

    def _render_background(self, surface: pygame.Surface, offset: tuple[int, int], root: View,
                           alpha: int = 255) -> NoReturn:
        rect = self.rect.move(*offset)
        if self.background:
            self.material_controller.set_material(self.background, self._style.material_transition)
        elif root.element_focused is self:
            self.material_controller.set_material(self._style.focus_material, self._style.material_transition)
        elif root.element_focused is not None and self in root.element_focused.get_parent_tree():
            self.material_controller.set_material(self._style.focus_child_material, self._style.material_transition)
        else:
            self.material_controller.set_material(self._style.material, self._style.material_transition)

        self.material_controller.render(self, surface, (
            rect.x - surface.get_abs_offset()[0],
            rect.y - surface.get_abs_offset()[1]),
                                        rect.size, alpha)

    def _render_elements(self, surface: pygame.Surface, offset: tuple[int, int], root: View,
                         alpha: int = 255) -> NoReturn:
        for i in self._elements[self._first_visible_element:]:
            i._render_a(surface, offset, root, alpha=alpha)
            if not i.is_visible:
                break

    def _event(self, event: pygame.event.Event, root: View) -> NoReturn:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if root.element_focused is self:
                    log.nav.info(self, "Enter key pressed, starting focus chain.")
                    with log.nav.indent:
                        root.element_focused = self._enter_in_first_element(root, 'in_first', ignore_self_focus=True)
                    log.nav.info(self, f"Focus chain ended. Focused {root.element_focused}.")

        for i in self._elements[self._first_visible_element:]:
            i._event(event, root)
            if not i.is_visible:
                break

    def _enter_in_first_element(self, root: View, key: str, ignore_self_focus: bool = False) -> Optional[Element]:
        pass

    def _set_style(self, style: StackStyle) -> NoReturn:
        self.set_style(style)

    def set_style(self, style: StackStyle) -> NoReturn:
        """
        Set the style of the Stack.
        """
        if style is None:
            if _c.default_stack_style is None:
                load_style(_c.DEFAULT_STYLE, parts=['stack'])
            self._style: StackStyle = _c.default_stack_style
        else:
            self._style: StackStyle = style

    elements = property(
        fget=lambda self: self._elements.copy(),
        doc="Returns the child elements of the Stack as a list. Read-only."
    )

    style = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The StackStyle of the Stack. Synonymous with the set_style() method."
    )
