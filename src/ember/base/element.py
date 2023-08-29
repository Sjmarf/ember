import abc

import pygame
import copy
from weakref import WeakSet
from typing import Union, TYPE_CHECKING, Optional, Sequence, Callable, Iterable, Type
from ember import log

from ember.event import (
    ELEMENTFOCUSED,
    ELEMENTUNFOCUSED,
    ELEMENTHOVERED,
    ELEMENTUNHOVERED,
)

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer
    from .container import Container

from ember.base.context_manager import ContextManager
from ember.animation.animation import Animation, AnimationContext
from ember.size import Size, SizeType, OptionalSequenceSizeType, FIT, FitSize
from ember.position import (
    PositionType,
    SequencePositionType,
    Position,
    DualPosition,
    CENTER,
)

from ember.trait import TraitValue, SizeTrait, PositionTrait

from ember import common as _c

from ..on_event import queue as on_event_queue


EmptyCallable = Callable[[], None]
MethodCallable = Callable[["Element"], None]


class CallbackRegistry:
    def __init__(self):
        self.calls: dict[Optional[int], set[str]] = {None: set()}

    def __getitem__(self, item: Optional[int]):
        return self.calls[item]

    def __bool__(self) -> bool:
        return len(self.calls) > 1 or bool(self.calls[None])

    def add_callback(self, event_types: Iterable[int], func: MethodCallable) -> None:
        if not event_types:
            self.calls[None].add(func.__name__)
            return

        for event_type in event_types:
            if event_type not in self.calls:
                self.calls[event_type] = set()
            if func.__name__ not in self.calls[event_type]:
                self.calls[event_type].add(func.__name__)

    def process_event(self, element: "Element", event_type: Optional[int]) -> None:
        for call in self.calls[None]:
            getattr(element, call)()
        if calls := self.calls.get(event_type):
            for call in calls:
                getattr(element, call)()

    def copy(self) -> "CallbackRegistry":
        new = copy.copy(self)
        new.calls = {k: v.copy() for k, v in self.calls.items()}
        return new

    def extend(self, registry: "CallbackRegistry") -> None:
        for event_type, calls in registry.calls.items():
            if event_type in self.calls:
                self.calls[event_type].update(calls)
            else:
                self.calls[event_type] = calls


class ElementMeta(abc.ABCMeta, type):
    def __init__(cls: Type["Element"], name, bases, attrs):
        super().__init__(name, bases, attrs)

        if on_event_queue or (
            len(bases) > 1
            and any(getattr(i, "_callback_registry", False) for i in bases)
        ):
            log.event_listener.line_break()
            with log.event_listener.indent(
                f"Creating new CallbackRegistry for {name}..."
            ):
                old_registry = cls._callback_registry
                log.event_listener.info(f"Registry copied from {bases[0].__name__}")
                cls._callback_registry = cls._callback_registry.copy()

                for base in bases:
                    if (
                        getattr(base, "_callback_registry", old_registry)
                        is not old_registry
                    ):
                        log.event_listener.info(
                            f"Adding callbacks from {base.__name__}"
                        )
                        cls._callback_registry.extend(base._callback_registry)

                for item in on_event_queue:
                    log.event_listener.info(
                        f"Adding queued callback {item[0].__name__}"
                    )
                    cls._callback_registry.add_callback(item[1], item[0])
                on_event_queue.clear()


class Element(abc.ABC, metaclass=ElementMeta):
    """
    The base element class. All UI elements in the library inherit from this class.
    """

    _trait_values: tuple[TraitValue] = ()
    _callback_registry: CallbackRegistry = CallbackRegistry()
    _instances = WeakSet()

    # ----------------------------

    x_: PositionTrait = PositionTrait(
        default_value=CENTER,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
    )
    x: Position = x_.value_descriptor()

    y_: PositionTrait = PositionTrait(
        default_value=CENTER,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
    )
    y: Position = y_.value_descriptor()

    w_: SizeTrait = SizeTrait(
        default_value=FIT,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
    )
    w: Size = w_.value_descriptor()

    h_: SizeTrait = SizeTrait(
        default_value=FIT,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
    )
    h: Size = h_.value_descriptor()

    # ----------------------------

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls._instances.add(instance)
        return instance

    def __init__(
        self,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        layer: Optional["ViewLayer"] = None,
        can_focus: bool = True,
    ):
        self.layer: Optional["ViewLayer"] = layer
        """
        The View that the Element is (directly or indirectly) attributed to.
        """

        self.parent: Optional["Container"] = None
        """
        The Container that the Element is directly attributed to. For example, if the Element is placed 
        inside of a VStack, it's :code:`parent` would be that VStack object.
        """

        self.ancestry: list["Container"] = []
        """
        A list containing the parent nodes of the element.
        """

        self.visible: bool = True
        """
        Is :code:`True` when any part of the element is visible on the screen. Read-only.
        """

        self.hovered: bool = True
        """
        Is :code:`True` when the mouse is hovered over the button. Read-only.
        """

        self.rect = pygame.FRect(0, 0, 0, 0)
        """
        A :code:`pygame.FRect` object containing the absolute position and size of the element. Read-only.
        """

        self._int_rect = pygame.Rect(0, 0, 0, 0)

        self._has_built: bool = False
        self._can_focus: bool = can_focus

        if rect is not None:
            x, y, w, h = rect[:]

        if pos is not None:
            if isinstance(pos, Sequence):
                x, y = pos
            elif isinstance(pos, DualPosition):
                x, y = pos.x, pos.y
            else:
                x, y = pos, pos

        self.x = x
        self.y = y

        if size is not None:
            if isinstance(size, Sequence):
                w, h = size
            else:
                w, h = size, size

        self._min_w: float = 0
        self._min_h: float = 0

        self.w = w
        self.h = h

        self._animation_contexts: list[AnimationContext] = []

        if ContextManager.context_stack[-1] is not None:
            ContextManager.context_stack[-1].context_queue.append(self)

    def build(self) -> None:
        if self._has_built:
            return
        self._has_built = True
        with log.size.indent("Building...", self):
            self._build()
        with log.size.indent("Built, starting chain up...", self):
            self.update_min_size(proprogate=False)

    def _build(self) -> None:
        """
        Used internally by the library.
        """

    def update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if self in self.layer.rect_update_queue:
            log.size.info(
                "Element is queued for update but recieved an update first, removing from list.",
                self,
            )
            self.layer.rect_update_queue = list(
                filter(lambda a: a is not self, self.layer.rect_update_queue)
            )

        if self.w.relies_on_other_value:
            if h != self.rect.h:
                log.size.info(
                    f"Height was changed and width calculation relies on height, queueing...",
                    self,
                )
                self.rect.update(x, y, w, h)
                self.update_rect_next_tick()
                return

        if self.h.relies_on_other_value:
            if w != self.rect.w:
                log.size.info(
                    f"Width was changed and height calculation relies on width, queueing...",
                    self,
                )
                self.rect.update(x, y, w, h)
                self.update_rect_next_tick()
                return

        if self.rect[:] == (x, y, w, h):
            log.size.info("Size didn't change, cutting chain...")
            return

        self.rect.update(x, y, w, h)
        self._int_rect.update(
            int(x),
            int(y),
            int(w),
            int(h),
        )

        with log.size.indent(
            f"Rect updated [{self.rect.x:.2f}, {self.rect.y:.2f}, {self.rect.w:.2f}, {self.rect.h:.2f}].",
            self,
        ):
            self._update_rect(surface, x, y, w, h)

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        pass

    def update_rect_next_tick(self) -> None:
        """
        On the next view update, call update_rect for this element.
        """
        if (
            self.layer
            and self.parent
            and self.parent not in self.layer.rect_update_queue
        ):
            log.size.info(
                f"Queued parent {self.parent} for rect update next tick.", self
            )
            self.layer.rect_update_queue.append(self.parent)
        else:
            log.size.info("No layer - could not queue rect update.", self)

    def update_min_size_next_tick(self, must_update_parent: bool = False) -> None:
        """
        On the next view update, call update_min_size for this element.
        """
        if self.layer and self not in self.layer.min_size_update_queue:
            log.size.info("Queued for min size update next tick.", self)
            self.layer.min_size_update_queue.append((self, must_update_parent))
        else:
            log.size.info("No layer - could not queue min size update.", self)

    def update_min_size(
        self, proprogate: bool = True, must_update_parent: bool = False
    ) -> None:
        old_w, old_h = self._min_w, self._min_h

        self._update_min_size()

        log.size.info(f"{self.w}, {self.h}, {self._min_w, self._min_h}")

        # If the container is not empty
        if self:
            match (
                self._min_w == 0 and isinstance(self.w, FitSize),
                self._min_h == 0 and isinstance(self.h, FitSize),
            ):
                case (False, False):
                    pass

                case (True, True):
                    raise _c.Error(
                        f"{type(self).__name__} has a FitSize width and FitSize height "
                        f"but no dependable child element was found on either dimension. "
                        f"At least one child element of the {type(self).__name__} must have a "
                        f"non-FillSize width and one child must have a non-FillSize height."
                    )

                case (True, False):
                    raise _c.Error(
                        f"{type(self).__name__} has a FitSize width "
                        f"but no dependable child element was found. At least one child element "
                        f"of the {type(self).__name__} must have a non-FillSize width."
                    )

                case (False, True):
                    raise _c.Error(
                        f"{type(self).__name__} has a FitSize height "
                        f"but no dependable child element was found. At least one child element "
                        f"of the {type(self).__name__} must have a non-FillSize height."
                    )

        cut_chain = False

        match (old_w != self._min_w, old_h != self._min_h):
            case (True, True):
                log.size.info(
                    f"Minimum size changed from {(old_w, old_h)} to "
                    f"{self._min_w, self._min_h}.",
                    self,
                )

            case (True, False):
                log.size.info(
                    f"Minimum width changed from {old_w} to {self._min_w}. Minimum height {self._min_h} not changed.",
                    self,
                )

            case (False, True):
                log.size.info(
                    f"Minimum height changed from {old_h} to {self._min_h}. Minimum width {self._min_w} not changed.",
                    self,
                )

            case _:
                log.size.info("Minimum size wasn't changed.", self)
                cut_chain = True

        # if self.parent is None or not (
        #     self.parent.w.relies_on_min_value or self.parent.h.relies_on_min_value
        # ):
        #     cut_chain = True

        if (proprogate and not cut_chain) or must_update_parent:
            if self.parent:
                self.update_rect_next_tick()

                with log.size.indent(f"-> parent."):
                    self.parent.update_min_size()
            else:
                log.size.info("No parent - cutting chain...", self)

    def _update_min_size(self) -> None:
        """
        Used internally by the library. Calling this method calls the same method for the container that the element
        is inside.
        """
        pass

    def render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used internally by the library. Renders the element, with transitions taken into consideration.

        """
        self._render(surface, offset, alpha=alpha)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used intenally by the library.
        """
        pass

    def update(self) -> None:
        """
        Used internally by the library. Updates the element, with transitions taken into consideration.
        """
        for anim_context in self._animation_contexts[:]:
            if anim_context._update():
                anim_context._finish()
                self._animation_contexts.remove(anim_context)

        if (hovered := self.rect.collidepoint(_c.mouse_pos)) != self.hovered:
            self.hovered = hovered
            if hovered:
                event = pygame.event.Event(ELEMENTHOVERED, element=self)
            else:
                event = pygame.event.Event(ELEMENTUNHOVERED, element=self)
            self._post_event(event)

        self._update()

    def _update(self) -> None:
        """
        Used intenally by the library.
        """
        pass

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        self.ancestry = ancestry
        log.ancestry.info(f"Updated ancestry.", self)

        if ancestry:
            self.parent = ancestry[-1]
            self.layer = self.parent.layer
        else:
            self.parent, self.layer = None, None

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        # 'previous' is used for going back up the chain - it is set to None when going downwards

        if direction in {
            _c.FocusDirection.IN,
            _c.FocusDirection.IN_FIRST,
            _c.FocusDirection.SELECT,
        }:
            log.nav.info("Returning self.")
            return self
        elif self.parent:
            # Go up a level and try again
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        """
        Called by the parent of the element for each Pygame event,
        with the pygame event object passed to the method.
        """
        return False

    def _animatable_value(self, func: callable, **kwargs) -> bool:
        if (anim := Animation.animation_stack[-1]) is not None:
            context = anim.create_context(self, func, kwargs)
            self._animation_contexts.append(context)
            return True
        return False

    def _post_event(self, event: pygame.event.Event) -> None:
        pygame.event.post(event)
        self._callback_registry.process_event(self, event.type)

    def get_abs_w(self, max_width: float = 0) -> float:
        """
        Get the width of the element as a float, given the maximum width to fill.
        """
        return self.w.get(self._min_w, max_width, self.rect.h)

    def get_abs_h(self, max_height: float = 0) -> float:
        """
        Get the height of the element as a float, given the maximum height to fill.
        """
        return self.h.get(self._min_h, max_height, self.rect.w)

    def focus(self) -> None:
        """
        Focuses the element. Only works if the element is inside a ViewLayer.
        """
        if self.layer:
            if self.layer.element_focused is not self:
                self.layer.element_focused = self
                event = pygame.event.Event(ELEMENTFOCUSED, element=self)
                self._post_event(event)
                if not self.visible:
                    self.parent.make_visible(self)
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
                event = pygame.event.Event(ELEMENTUNFOCUSED, element=self)
                self._post_event(event)
        else:
            raise _c.Error(
                f"Cannot unfocus {self} because element is not inside of a ViewLayer."
            )

    @property
    def focused(self) -> bool:
        return self.layer.element_focused is self

    @focused.setter
    def focused(self, value: bool):
        if value:
            self.focus()
        else:
            self.unfocus()

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new
