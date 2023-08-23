from typing import TypeVar, TYPE_CHECKING, Optional, Callable
from contextlib import contextmanager
import itertools

import pygame.event

if TYPE_CHECKING:
    from ember.ui.base.mixin.style import Style
    from .style import Style

from ember.trait.trait import Trait
from .. import log

from ember.event_listener import EventListener

T = TypeVar("T", bound="Style", covariant=True)
ListenerCallable = Callable[[T, Optional[pygame.Event]], None]

class State(EventListener[T]):
    inspected_element: Optional["Style"] = None

    def __init__(
        self,
        active_by_default: bool = False,
        priority: float = 0,
        activation_triggers: Optional[list[int]] = None,
        deactivation_triggers: Optional[list[int]] = None,
        on_become_active: Optional[ListenerCallable] = None,
        on_become_primary: Optional[ListenerCallable] = None,
        on_become_deactive: Optional[ListenerCallable] = None,
        name: Optional[str] = None,
    ):
        self.active_by_default: bool = active_by_default
        self.priority: float = priority
        self.style: Optional["Style"] = None
        self.name: Optional[str] = name

        self.activation_triggers: list[int] = (
            [] if activation_triggers is None else activation_triggers
        )
        self.deactivation_triggers: list[int] = (
            [] if deactivation_triggers is None else deactivation_triggers
        )
        self.on_become_active_callable: Optional[ListenerCallable] = on_become_active
        self.on_become_primary_callable: Optional[ListenerCallable] = on_become_primary
        self.on_become_deactive_callable: Optional[
            ListenerCallable
        ] = on_become_deactive
        super().__init__()

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<State('{self.name}')>"
        return "<State>"

    def process_event(self, element: "Style", event: pygame.event.Event) -> None:
        if event.type in self.activation_triggers:
            log.style.line_break()
            with log.style.indent("Activation trigger recieved...", self):
                self.activate(element, event)
        if event.type in self.deactivation_triggers:
            log.style.line_break()
            with log.style.indent("Deactivation trigger recieved...", self):
                self.deactivate(element, event)
        super().process_event(element, event)

    def on_become_active(self, func: ListenerCallable) -> ListenerCallable:
        self.on_become_active_callable = func
        return func

    def on_become_primary(self, func: ListenerCallable) -> ListenerCallable:
        self.on_become_primary_callable = func
        return func

    def on_become_deactive(self, func: ListenerCallable) -> ListenerCallable:
        self.on_become_deactive_callable = func
        return func

    def is_active(self, element: Optional["Style"] = None) -> bool:
        if element is None:
            element = self.inspected_element
        return self in itertools.chain(
            element._styles[self.style], element._styles[None]
        )

    def activate(
        self,
        element: Optional["Style"] = None,
        event: Optional[pygame.Event] = None,
    ) -> None:
        with log.style.indent(f"Activated for {element}...", self):
            if element is None:
                element = self.inspected_element
            if self in element._styles[self.style]:
                return
            with Trait.inspecting(Trait.Layer.STYLE), self.inspecting(element):
                element._styles[self.style].append(self)
                element._styles[self.style].sort(key=lambda x: x.priority)
                if self.on_become_active_callable is not None:
                    self.on_become_active_callable(element, event)
                if (
                    self.on_become_primary_callable is not None
                    and self == element._styles[self.style][-1]
                ):
                    self.on_become_primary_callable(element, event)

    def deactivate(
        self,
        element: Optional["Style"] = None,
        event: Optional[pygame.Event] = None,
    ) -> None:
        with log.style.indent(f"Deactivated for {element}...", self):
            if element is None:
                element = self.inspected_element
            if self not in element._styles[self.style]:
                return
            with Trait.inspecting(Trait.Layer.STYLE), self.inspecting(element):
                primary_state = (
                    element._styles[self.style][-1]
                    if element._styles[self.style]
                    else None
                )
                element._styles[self.style].remove(self)
                if (
                    element._styles[self.style]
                    and element._styles[self.style][-1] != primary_state
                ):
                    if (
                        element._styles[self.style][-1].on_become_primary_callable
                        is not None
                    ):
                        element._styles[self.style][-1].on_become_primary_callable(
                            element, event
                        )
                if self.on_become_deactive_callable is not None:
                    self.on_become_deactive_callable(element, event)

    @classmethod
    @contextmanager
    def inspecting(cls, element: "Style") -> None:
        cls.inspected_element = element
        yield
        cls.inspected_element = None
