import abc

import pygame
import copy
from weakref import WeakSet
from typing import Union, TYPE_CHECKING, Optional, Sequence, Callable
from ember import log
from .element_min_size import ElementMinSize

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer
    from .container import Container
    from .can_pivot import CanPivot

from ember.ui.context_manager import ContextManager
from ember.animation.animation import AnimationContext, Animation
from ember.size import Size, SizeType, OptionalSequenceSizeType, FIT, FitSize
from ember.position import (
    Position,
    PositionType,
    SequencePositionType,
    DualPosition,
    CENTER,
)

from ember.trait import Trait
from ember.size import load_size
from ember.position import load_position
from ember.trait.cascading_trait_value import CascadingTraitValue

from ember import common as _c
from ember import axis as axis_module
from ember.axis import HORIZONTAL

from .element_meta import ElementMeta
from ember.callback_registry import CallbackRegistry


EmptyCallable = Callable[[], None]
MethodCallable = Callable[["Element"], None]


class Element(abc.ABC, metaclass=ElementMeta):
    """
    The base element class. All UI elements in the library inherit from this class.
    """

    # This attribute is set inside of can_pivot.py to avoid a circular import
    _CanPivot: type["CanPivot"]

    _traits: tuple[Trait] = ()
    _callback_registry: CallbackRegistry = CallbackRegistry()
    _instances = WeakSet()

    # ----------------------------

    def _geometry_trait_modified(self, trait_name: str) -> None:
        with log.size.indent(f"Trait '{trait_name}' modified:"):
            self.update_min_size_next_tick(must_update_parent=True)

    x: Trait[Position] = Trait(
        default_value=CENTER,
        on_update=lambda self: self._geometry_trait_modified("x"),
        default_cascade_depth=1,
        load_value_with=load_position,
    )

    y: Trait[Position] = Trait(
        default_value=CENTER,
        on_update=lambda self: self._geometry_trait_modified("y"),
        default_cascade_depth=1,
        load_value_with=load_position,
    )

    w: Trait[Size] = Trait(
        default_value=FIT,
        on_update=lambda self: self._geometry_trait_modified("w"),
        default_cascade_depth=1,
        load_value_with=load_size,
    )

    h: Trait[Size] = Trait(
        default_value=FIT,
        on_update=lambda self: self._geometry_trait_modified("h"),
        default_cascade_depth=1,
        load_value_with=load_size,
    )

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
        can_focus: bool = False,
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

        self._min_size: ElementMinSize = ElementMinSize()

        self.w = w
        self.h = h

        self._animation_contexts: list[AnimationContext] = []

        if ContextManager.context_stack[-1] is not None:
            ContextManager.context_stack[-1].context_queue.append(self)

        if CascadingTraitValue.context_depth > 0:
            CascadingTraitValue.new_elements.append(self)

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
        self,
        surface: pygame.Surface,
        x: Optional[float] = None,
        y: Optional[float] = None,
        w: Optional[float] = None,
        h: Optional[float] = None,
        rel_pos1: Optional[float] = None,
        rel_pos2: Optional[float] = None,
        rel_size1: Optional[float] = None,
        rel_size2: Optional[float] = None,
    ) -> None:
        if isinstance(self.parent, Element._CanPivot):
            if self.parent.axis == HORIZONTAL:
                if rel_pos1 is not None:
                    x = rel_pos1
                if rel_pos2 is not None:
                    y = rel_pos2
                if rel_size1 is not None:
                    w = rel_size1
                if rel_size2 is not None:
                    h = rel_size2
            else:
                if rel_pos2 is not None:
                    x = rel_pos2
                if rel_pos1 is not None:
                    y = rel_pos1
                if rel_size2 is not None:
                    w = rel_size2
                if rel_size1 is not None:
                    h = rel_size1

        if None in (x, y, w, h):
            raise ValueError(
                f"Missing value for updated element geometry - ({x}, {y}, {w}, {h})"
            )

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
            f"Rect updating: [{self.rect.x:.2f}, {self.rect.y:.2f}, {self.rect.w:.2f}, {self.rect.h:.2f}].",
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
            self.layer is not None
            and self.parent is not None
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
        if self.layer is not None and self not in self.layer.min_size_update_queue:
            log.size.info("Queued for min size update next tick.", self)
            self.layer.min_size_update_queue.append((self, must_update_parent))
        else:
            log.size.info("No layer - could not queue min size update.", self)

    def update_min_size(
        self, proprogate: bool = True, must_update_parent: bool = False
    ) -> None:
        old_w, old_h = self._min_size.w, self._min_size.h

        self._update_min_size()

        # If the container is not empty
        if getattr(self, "_elements_to_render", False):
            match (
                self._min_size.w == 0 and isinstance(self.w, FitSize),
                self._min_size.h == 0 and isinstance(self.h, FitSize),
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

        match (old_w != self._min_size.w, old_h != self._min_size.h):
            case (True, True):
                log.size.info(
                    f"Minimum size changed from {(old_w, old_h)} to "
                    f"{self._min_size.w, self._min_size.h}.",
                    self,
                )

            case (True, False):
                log.size.info(
                    f"Minimum width changed from {old_w} to {self._min_size.w}. Minimum height {self._min_size.h} not changed.",
                    self,
                )

            case (False, True):
                log.size.info(
                    f"Minimum height changed from {old_h} to {self._min_size.h}. Minimum width {self._min_size.w} not changed.",
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
            if self.parent is not None:
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

    def render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used internally by the library.
        """
        self._render(surface, offset, alpha=alpha)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used intenally by the library.
        """

    def update(self) -> None:
        """
        Used internally by the library. Updates the element, with transitions taken into consideration.
        """
        for anim_context in self._animation_contexts[:]:
            if anim_context._update():
                anim_context._finish()
                self._animation_contexts.remove(anim_context)
        self._update()

    def _update(self) -> None:
        """
        Used intenally by the library.
        """

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        self.ancestry = ancestry
        log.ancestry.info(f"Updated ancestry.", self)

        if ancestry:
            self.parent = ancestry[-1]
            self.layer = self.parent.layer
        else:
            self.parent, self.layer = None, None

    def update_cascading_value(self, value: CascadingTraitValue, depth: int) -> None:
        if isinstance(self, value.ref.owner):
            setattr(self, value.ref.trait.name, value.value)
            log.cascade.info(
                f"Value set to {getattr(self, value.ref.trait.name)}, with animation {Animation.animation_stack[-1]}",
                self,
            )
        else:
            log.cascade.info(f"Not an instance of {value.ref.owner}, did not set", self)

    def event(self, event: pygame.event.Event) -> bool:
        return self._event(event)

    def _event(self, event: pygame.event.Event) -> bool:
        """
        Called by the parent of the element for each Pygame event,
        with the pygame event object passed to the method.
        """
        return False

    def _post_event(self, event: Union[pygame.event.Event, int]) -> None:
        if isinstance(event, int):
            event = pygame.event.Event(event, element=self)
        pygame.event.post(event)
        self._callback_registry.process_event(self, event.type)

    def get_x(
        self, container_width: float, element_width: Optional[float] = None
    ) -> float:
        return self.x.get(
            container_width, self.rect.w if element_width is None else element_width
        )

    def get_y(
        self, container_height: float, element_height: Optional[float] = None
    ) -> float:
        return self.y.get(
            container_height, self.rect.h if element_height is None else element_height
        )

    def get_w(self, max_width: float = 0) -> float:
        """
        Get the width of the element as a float, given the maximum width to fill.
        """
        return self.w.get(
            self._min_size.w, max_width, self.rect.h, axis_module.VERTICAL
        )

    def get_h(self, max_height: float = 0) -> float:
        """
        Get the height of the element as a float, given the maximum height to fill.
        """
        return self.h.get(
            self._min_size.h, max_height, self.rect.w, axis_module.VERTICAL
        )

    @property
    def _pivotable_parent(self) -> "_CanPivot":
        if isinstance(self.parent, Element._CanPivot):
            return self.parent
        raise _c.Error(
            "Parent is not a subclass of CanPivot - cannot determine parent axis."
        )

    def get_abs_rel_size1(self, max_size: float = 0) -> float:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.get_w(max_size)
        return self.get_h(max_size)

    def get_abs_rel_size2(self, max_size: float = 0) -> float:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.get_h(max_size)
        return self.get_w(max_size)

    @property
    def rel_pos1(self) -> Position:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.x
        return self.y

    @property
    def rel_pos2(self) -> Position:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.y
        return self.x

    @property
    def rel_size1(self) -> Size:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.w
        return self.h

    @property
    def rel_size2(self) -> Size:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.h
        return self.w

    def is_animating(self, trait: Trait) -> bool:
        return any(i.trait_context.trait == trait for i in self._animation_contexts)

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new
