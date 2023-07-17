import abc

import pygame
import inspect
import copy
import warnings
from typing import Union, TYPE_CHECKING, Optional, Sequence
from ember import log

from ember.event import TRANSITIONFINISHED, ELEMENTUNFOCUSED, ELEMENTFOCUSED

if TYPE_CHECKING:
    from ember.ui.view import View, ViewLayer
    from ember.transition.transition import Transition, TransitionController
    from ...style.style import Style

from .context_manager import ContextManagerMixin
from ...animation.animation import Animation, AnimationContext
from ember.size import (
    Size,
    SizeType,
    SequenceSizeType,
    OptionalSequenceSizeType,
    load_size,
)
from ember.position import PositionType, SequencePositionType, Position, DualPosition

from ... import common as _c


class Element(abc.ABC):
    """
    The base element class. All UI elements in the library inherit from this class.
    """

    def __init__(
        self,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        default_size: Optional[SequenceSizeType] = None,
        can_focus: bool = True,
    ):
        self.layer: Optional[ViewLayer] = None
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

        self.rect = pygame.FRect(0, 0, 0, 0)
        """
        A :code:`pygame.FRect` object containing the absolute position and size of the element. Read-only.
        """

        self._int_rect = pygame.Rect(0, 0, 0, 0)

        self._has_built: bool = False
        self._can_focus: bool = can_focus
        self._transition: Optional["TransitionController"] = None

        if rect is not None:
            x, y, w, h = rect[:]

        if pos is not None:
            if isinstance(pos, Sequence):
                x, y = pos
            elif isinstance(pos, DualPosition):
                x, y = pos.x, pos.y
            else:
                x, y = pos, pos

        self.set_pos(x, y, _update=False)

        if size is not None:
            if isinstance(size, Sequence):
                w, h = size
            else:
                w, h = size, size

        self._min_w: float = 0
        self._min_h: float = 0

        if default_size is None:
            default_size = self._style.size

        if not isinstance(default_size, Sequence):
            default_size = default_size, default_size

        self._default_w: Optional[Size] = default_size[0]
        self._default_h: Optional[Size] = default_size[1]

        self._w: Size = load_size(w)
        self._h: Size = load_size(h)

        self._active_w: Optional[Size] = None
        self._active_h: Optional[Size] = None
        self.set_active_w()
        self.set_active_h()

        self._animation_contexts: list[AnimationContext] = []

        if ContextManagerMixin.context_stack[-1] is not None:
            ContextManagerMixin.context_stack[-1].context_queue.append(self)

    def _build_chain(self) -> None:
        """
        Used internally by the library. Calling this method calls the same method for the element's child elements.
        """
        if self._has_built:
            return
        self._has_built = True
        log.size.info(self, "Element built, starting chain up without proprogation.")
        with log.size.indent:
            self._update_rect_chain_up(_update=False)

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        """
        Used internally by the library. Calling this method calls the same method for the element's child elements.
        """

        self.rect.update(x, y, w, h)
        self._int_rect.update(
            int(x),
            int(y),
            int(w),
            int(h),
        )

        log.size.info(self, f"Chain down {self.rect[:]}, visible = {self.is_visible}.")

    @staticmethod
    def _chain_up_decorator(func: callable) -> callable:
        def wrapper(self, _update: bool = True) -> None:
            old_w, old_h = self._min_w, self._min_h
            log.size.info(self, "Chain up.")
            cut_chain = False

            func(self)

            if old_w != self._min_w and old_h != self._min_h:
                log.size.info(
                    self,
                    f"Minimum size changed from {(old_w, old_h)} to "
                    f"{self._min_w, self._min_h}.",
                )
            elif old_w != self._min_w:
                log.size.info(
                    self,
                    f"Minimum width changed from {old_w} to {self._min_w}. Fit height {self._min_h} not changed.",
                )
            elif old_h != self._min_h:
                log.size.info(
                    self,
                    f"Minimum height changed from {old_h} to {self._min_h}. Fit width {self._min_w} not changed.",
                )
            else:
                cut_chain = False # True

            if not _update:
                log.size.info(self, "_update is False - cutting chain...")

            elif self.parent:
                if cut_chain:
                    log.size.info(self, "Size wasn't changed - cutting chain...")
                else:
                    log.size.info(self, f"-> parent.")
                    with log.size.indent:
                        self.parent._update_rect_chain_up()
            else:
                log.size.info(self, "No parent - cutting chain...")

            if self.layer:
                if self.layer._chain_down_from is None:
                    log.size.info(self, "Starting chain down next tick...")
                self.layer._chain_down_from = self.parent
            else:
                log.size.info(self, "No layer - check_size was not set.")

        return wrapper

    @_chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        """
        Used internally by the library. Calling this method calls the same method for the container that the element
        is inside.
        """
        pass

    def _render_a(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used internally by the libray. Renders the element, with transitions taken into consideration.
        :param offset:
        :param surface:
        :param alpha:
        :return:
        """

        if self._transition is not None:
            self._transition.render(surface, offset, alpha=alpha)
        else:
            self._render(surface, offset, alpha=alpha)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used intenally by the library.
        """
        pass

    def _update_a(self) -> None:
        """
        Used internally by the library. Updates the element, with transitions taken into consideration.
        """
        for anim_context in self._animation_contexts[:]:
            if anim_context._update():
                anim_context._finish()
                self._animation_contexts.remove(anim_context)

        if self._transition is not None:
            self._transition.update()
            if self._transition.timer <= 0:
                new_event = pygame.event.Event(
                    TRANSITIONFINISHED, element=self, controller=self._transition
                )
                self._transition = None
                pygame.event.post(new_event)
        else:
            self._update()

    def _update(self) -> None:
        """
        Used intenally by the library.
        """
        pass

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        """
        Sets the 'layer' attribute of the element, and all of its children, to the specified ViewLayer.
        """
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        # 'previous' is used for going back up the chain - it is set to None when going downwards

        if direction in {
            _c.FocusDirection.IN,
            _c.FocusDirection.IN_FIRST,
            _c.FocusDirection.SELECT,
        }:
            log.nav.info(self, "Returning self.")
            return self
        elif self.parent:
            # Go up a level and try again
            log.nav.info(self, f"-> Parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        """
        Called by the parent of the element for each Pygame event,
        with the pygame event object passed to the method.
        """
        return False

    def _on_unfocus(self) -> None:
        """
        Called by ViewLayer when the element is unfocused. For internal use only.
        """
        pass

    def _set_parent(self, parent: Union["Element", "ViewLayer"]) -> None:
        """
        Used internally by the library. You don't need to call this.
        """
        self.parent = parent

    def _animatable_value(self, func: callable, **kwargs) -> bool:
        if (anim := Animation.animation_stack[-1]) is not None:
            context = anim.create_context(self, func, kwargs)
            self._animation_contexts.append(context)
            return True
        return False

    def set_pos(self, *pos: Optional[SequencePositionType], _update=True) -> None:
        """
        Set the position of the element.
        """
        if isinstance(pos[0], Sequence):
            pos = pos[0]

        if not isinstance(pos, Sequence):
            pos = (pos, pos)

        self._x: Position = Position._load(pos[0])
        self._y: Position = Position._load(pos[1])
        if _update:
            self._update_rect_chain_up()

    def set_x(self, value: Optional[PositionType], _update=True) -> None:
        """
        Set the x position of the element.
        """
        new_val = Position._load(value)
        if not self._animatable_value(self.set_x, value=(self._x, new_val)):        
            self._x: Position = new_val
            if _update:
                self._update_rect_chain_up()

    def set_y(self, value: Optional[PositionType], _update=True) -> None:
        """
        Set the y position of the element.
        """
        self._y: Position = Position._load(value)
        if _update:
            self._update_rect_chain_up()

    def set_size(self, *size: OptionalSequenceSizeType, _update=True) -> None:
        """
        Set the size of the element.
        """
        
        if isinstance(size[0], Sequence):
            size = size[0]
        
        if len(size) == 1:
            size = size[0], size[0]
        
        self.set_w(size[0], _update=_update)
        self.set_h(size[1], _update=_update)

    def set_w(self, value: SizeType, _update=True) -> None:
        """
        Set the width of the element.
        """
        new_val = load_size(value)
        if not self._animatable_value(self.set_w, value=(self._active_w, new_val)):
            self._w = new_val
            if _update:
                self._update_rect_chain_up()

    def set_h(self, value: SizeType, _update=True) -> None:
        """
        Set the height of the element.
        """
        new_val = load_size(value)
        if not self._animatable_value(self.set_h, value=(self._active_h, new_val)):        
            self._h = new_val
            if _update:
                self._update_rect_chain_up()

    def get_size(self) -> tuple[Size, Size]:
        """
        Get the size of the element. Returns ember.size.Size objects.
        If you want float sizes, use get_abs_size() instead.
        """
        return self._w, self._h

    def get_w(self) -> Size:
        """
        Get the width of the element. Returns ember.size.Size object.
        If you want the width as a float, use get_abs_w() instead.
        """
        return self._w

    def get_h(self) -> Size:
        """
        Get the height of the element. Returns ember.size.Size object.
        If you want the height as a float, use get_abs_h() instead.
        """
        return self._h

    def get_abs_w(self, max_width: float = 0) -> float:
        """
        Get the width of the element as a float, given the maximum width to fill.
        """
        return self._active_w.get(self._min_w, max_width)

    def get_abs_h(self, max_height: float = 0) -> float:
        """
        Get the height of the element as a float, given the maximum height to fill.
        """
        return self._active_h.get(self._min_h, max_height)

    def set_active_w(self, *sizes: Optional[Size]) -> None:
        if self._w is not None:
            self._active_w = self._w
            return
        for i in sizes:
            if i is not None:
                self._active_w = i
                return
        self._active_w = self._default_w

    def set_active_h(self, *sizes: Optional[Size]) -> None:
        if self._h is not None:
            self._active_h = self._h
            return
        for i in sizes:
            if i is not None:
                self._active_h = i
                return
        self._active_h = self._default_h

    def focus(self) -> None:
        """
        Focuses the element. Only works if the element is inside a ViewLayer.
        """
        if self.layer:
            if self.layer.element_focused is not self:
                self.layer.element_focused = self
                event = pygame.event.Event(ELEMENTFOCUSED, element=self)
                pygame.event.post(event)
        else:
            raise _c.Error(
                f"Cannot focus {self} because element is not inside of a ViewLayer."
            )

    def unfocus(self) -> None:
        """
        Unfocuses the element.
        """
        if self.layer:
            if self.layer.element_focused is self:
                self.layer.element_focused = None
                self._on_unfocus()
                event = pygame.event.Event(ELEMENTUNFOCUSED, element=self)
                pygame.event.post(event)
        else:
            raise _c.Error(
                f"Cannot unfocus {self} because element is not inside of a ViewLayer."
            )

    def get_parent_tree(self) -> list["Element"]:
        """
        Returns a list of ancestors, starting with the element's parent, then it's grandparent, and so on.
        """
        warnings.warn("get_parent_tree is Deprecated.", DeprecationWarning)
        parents = [self.parent]
        while True:
            if not hasattr(parents[-1], "parent"):
                break
            next_parent = parents[-1].parent
            if not hasattr(next_parent, "parent"):
                break
            parents.append(next_parent)
        return parents

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new


ElementStrType = Union[str, Element, None]
