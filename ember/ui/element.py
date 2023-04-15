import pygame
import math
import copy
from typing import Union, TYPE_CHECKING, Optional, Sequence, NoReturn
from ember import log

import ember.event

if TYPE_CHECKING:
    from ember.ui.view import View
    from ember.transition.transition import Transition

from ember.size import Size, SizeType, SequenceSizeType


class Element:
    def __init__(self,
                 size: SequenceSizeType = (20, 20),
                 width: SizeType = 20,
                 height: SizeType = 20,
                 default_size: Sequence[SizeType] = (20, 20),
                 can_focus=True):

        """
        The base element class. All elements in the library inherit from this class.

        :param size:
        :param width:
        :param height:
        :param default_size:
        :param can_focus:
        """

        self.root: Optional[View] = None
        """
        The View that the Element is (directly or indirectly) attributed to.
        """

        self.parent: Optional[Element] = None
        """
        The Element or View that the Element is directly attributed to. For example, if the Element is placed 
        inside of a VStack, it's :code:`parent` would be that VStack object.
        """

        self.is_visible: bool = True
        """
        Is :code:`True` when any part of the element is visible on the screen. Read-only.
        """

        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        """
        A :code:`pygame.Rect` object containing the position and size of the element. Read-only.
        """

        self._disabled: bool = False
        self._transition: Optional[Transition] = None
        self._can_focus: bool = can_focus

        if size is None:
            if width is None:
                width = default_size[0]

            if height is None:
                height = default_size[1]
        else:
            if isinstance(size, Sequence):
                width, height = size
            else:
                width, height = size, size

        self.set_size(width, height, _update_rect_chain_up=False)

    @staticmethod
    def _chain_up_decorator(func: callable) -> callable:
        def wrapper(self) -> NoReturn:
            old_width, old_height = self._fit_width, self._fit_height
            log.size.info(self, "Chain up.")

            func(self)

            if old_width != self._fit_width and old_height != self._fit_height:
                log.size.info(self, f"Fit size changed from {(old_width, old_height)} to "
                                    f"{self._fit_width, self._fit_height}.")
            elif old_width != self._fit_width:
                log.size.info(self, f"Fit width changed from {old_width} to {self._fit_width}.")
            elif old_height != self._fit_height:
                log.size.info(self, f"Fit width changed from {old_height} to {self._fit_height}.")
            else:
                return

            if self.parent:
                self.parent._update_rect_chain_up()
                self.root.check_size = True

        return wrapper

    def set_size(self, *size: Union[Sequence[SizeType], SizeType], _update_rect_chain_up=True) -> NoReturn:
        """
        Set the size of the element.
        """
        if isinstance(size[0], Sequence):
            size = size[0]

        self._width: Size = Size(size[0]) if isinstance(size[0], (int, float)) else size[0]
        self._height: Size = Size(size[-1]) if isinstance(size[1], (int, float)) else size[1]
        if _update_rect_chain_up:
            self._update_rect_chain_up()

    def set_width(self, value: SizeType, _update_rect_chain_up=True) -> NoReturn:
        """
        Set the width of the element.
        """
        self._width: Size = Size(value) if isinstance(value, (int, float)) else value
        if _update_rect_chain_up:
            self._update_rect_chain_up()

    def set_height(self, value: SizeType, _update_rect_chain_up=True) -> NoReturn:
        """
        Set the height of the element.
        """
        self._height: Size = Size(value) if isinstance(value, (int, float)) else value
        if _update_rect_chain_up:
            self._update_rect_chain_up()

    def get_size(self) -> tuple[Size, Size]:
        """
        Get the size of the element. Returns ember.size.Size objects.
        If you want float sizes, use get_abs_size() instead.
        """
        return self._width, self._height

    def get_width(self) -> Size:
        """
        Get the width of the element. Returns ember.size.Size object.
        If you want the width as a float, use get_abs_width() instead.
        """

    def get_height(self) -> Size:
        """
        Get the height of the element. Returns ember.size.Size object.
        If you want the height as a float, use get_abs_height() instead.
        """

    def get_abs_size(self, max_size: Sequence[float] = (0, 0)) -> tuple[float, float]:
        """
        Get the size of the element as floats, given the maximum space to fill.
        """
        return self.get_abs_width(max_size[0]), self.get_abs_height(max_size[1])

    def get_abs_width(self, max_width: float = 0, _ignore_fill_width: bool = False) -> float:
        """
        Get the width of the element as a float, given the maximum width to fill.
        """
        if self._width.mode == 2:
            if _ignore_fill_width:
                return max_width
            return max_width * self._width.percentage + self._width.value
        elif self._width.mode == 1:
            if hasattr(self, "_fit_width"):
                return self._fit_width + self._width.value
            else:
                raise AttributeError(f"Element of type '{type(self).__name__}' cannot have a FIT width.")
        else:
            return self._width.value

    def get_abs_height(self, max_height: float = 0, _ignore_fill_height: bool = False) -> float:
        """
        Get the height of the element as a float, given the maximum height to fill.
        """
        if self._height.mode == 2:
            if _ignore_fill_height:
                return max_height
            return max_height * self._height.percentage + self._height.value
        elif self._height.mode == 1:
            if hasattr(self, "_fit_height"):
                return self._fit_height + self._height.value
            else:
                raise AttributeError(f"Element of type '{type(self).__name__}' cannot have a FIT height.")
        else:
            return self._height.value

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:
        """
        Used internally by the library. Calling this method calls the same method for the element's child elements.
        """

        self.rect.update(round(pos[0]), round(pos[1]),
                         round(self.get_abs_width(max_size[0], _ignore_fill_width=_ignore_fill_width)),
                         round(self.get_abs_height(max_size[1], _ignore_fill_height=_ignore_fill_height)))
        log.size.info(self, f"Chain down {self.rect[:]}.")

    def _update_rect_chain_up(self) -> NoReturn:
        """
        Used internally by the library. Calling this method calls the same method for the container that the element
        is inside.
        """
        pass

    def _update_a(self, root: "View") -> NoReturn:
        """
        Used internally by the library. Updates the element, with transitions taken into consideration.
        """
        if self._transition is not None:
            self._transition.update(root)
            if self._transition.timer <= 0:
                self._transition = None
                new_event = pygame.event.Event(ember.event.TRANSITIONFINISHED, element=self)
                pygame.event.post(new_event)
        else:
            self._update(root)

    def _update(self, root: "View") -> NoReturn:
        """
        Used intenally by the library.
        """
        pass

    def _render_a(self, surface: pygame.Surface, offset: tuple[int, int], root: "View",
                  alpha: int = 255) -> NoReturn:
        """
        Used internally by the libray. Renders the element, with transitions taken into consideration.
        :param offset:
        :param surface:
        :param alpha:
        :param root:
        :return:
        """

        if self._transition is not None:
            self._transition.render(surface, offset, root, alpha=alpha)
        else:
            self._render(surface, offset, root, alpha=alpha)

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View",
                alpha: int = 255) -> NoReturn:
        """
        Used intenally by the library.
        """
        pass

    def _set_parent(self, parent: Union["Element", "View"]) -> NoReturn:
        """
        Used internally by the library. You don't need to call this.
        """
        self.parent = parent

    def _set_root(self, root: "View") -> NoReturn:
        """
        Used internally by the library. You don't need to call this.
        """
        self.root = root

    def _on_unfocus(self) -> NoReturn:
        """
        Used internally by the library.
        """
        # Called by View when the element is unfocused
        pass

    def get_parent_tree(self) -> list["Element"]:
        """
        Returns a list of ancestors, starting with the element's parent, then it's grandparent, and so on.
        """
        parents = [self.parent]
        while True:
            if not hasattr(parents[-1], "parent"):
                break
            next_parent = parents[-1].parent
            if not hasattr(next_parent, "parent"):
                break
            parents.append(next_parent)
        return parents

    def _focus_chain(self, root: "View", previous: "Element" = None, direction: str = 'in') -> "Element":
        """
        Used internally by the library to manage keyboard/controller navigation.
        """
        # 'previous' is used for going back up the chain - it is set to None when going downwards
        if direction in {'in', 'in_first'}:
            log.nav.info(self, "Returning self.")
            return self
        elif self.parent:
            # Go up a level and try again
            log.nav.info(self, f"-> Parent {self.parent}.")
            return self.parent._focus_chain(root, self, direction=direction)

    def set_disabled(self, value: bool) -> NoReturn:
        """
        Disabled objects cannot be interacted with.
        """
        # This has to be a method, and not just a setattr lambda, because some subclasses replace it
        self._disabled = value

    def copy(self):
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new

    disabled = property(
        fget=lambda self: self._disabled,
        fset=set_disabled,
        doc="Disabled objects cannot be interacted with."
    )

    def _event(self, event: pygame.event.Event, root: "View"):
        pass


ElementStrType = Union[str, Element, None]
