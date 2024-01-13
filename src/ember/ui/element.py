import abc

import pygame
import copy
from weakref import WeakSet
from typing import Union, TYPE_CHECKING, Optional, Sequence, Callable
from ember import log

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer
    from .container import Container
    from .can_pivot import CanPivot
    from .has_geometry import HasGeometry

from ember.ui.context_manager import ContextManager
from ember.animation.animation import AnimationContext, Animation

from ember.trait import Trait
from ember.trait.cascading_trait_value import CascadingTraitValue

from ember import common as _c

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

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls._instances.add(instance)
        return instance

    def __init__(self, layer: Optional["ViewLayer"] = None):
        self._has_built: bool = False

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

        if ContextManager.context_stack[-1] is not None:
            ContextManager.context_stack[-1].context_queue.append(self)

    def build(self) -> None:
        if self._has_built:
            return
        self._has_built = True
        self._build()

    def _build(self) -> None:
        """
        Used internally by the library.
        """

    @abc.abstractmethod
    def unpack(self) -> tuple["HasGeometry", ...]:
        ...

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

    def _post_event(self, event: Union[pygame.event.Event, int]) -> None:
        if isinstance(event, int):
            event = pygame.event.Event(event, element=self)
        pygame.event.post(event)
        self._callback_registry.process_event(self, event.type)

    @property
    def _pivotable_parent(self) -> "CanPivot":
        if isinstance(self.parent, Element._CanPivot):
            return self.parent
        raise _c.Error(
            "Parent is not a subclass of CanPivot - cannot determine parent axis."
        )

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new

    def kill(self) -> None:
        """
        Remove the element from its parent container. Fails gracefully without raising an exception if the element doesn't have a parent.
        """
        if self.parent is not None:
            self.parent.remove_child(self)
