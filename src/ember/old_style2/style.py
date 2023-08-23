from typing import Type, TYPE_CHECKING, TypeVar, Optional, get_args, Callable, Generator

import pygame

from .state import State

from ember import common as _c
from .. import log
from ember.event_listener import EventListener

if TYPE_CHECKING:
    from ..ui.base.mixin.style import Style

T = TypeVar("T", bound="Element", covariant=True)
ListenerCallable = Callable[[T, Optional[pygame.Event]], None]


class Style(EventListener[T]):
    def __init__(
            self,
            *states: State[T],
    ):
        self.states: list[State[T]] = list(states)
        for state in self.states:
            if state.style is None:
                state.style = self
            else:
                raise _c.Error(
                    "A State object can only be attributed to 0 or 1 Styles, not 2."
                )

        self.active_callable: Optional[ListenerCallable] = None
        self.deactive_callable: Optional[ListenerCallable] = None
        super().__init__()

    def set_as_default(self, cls: Optional[Type[T]] = None) -> "Style":
        if cls is None:
            if (args := get_args(type(self).__orig_bases__[0])) and args[0] is not T:
                cls = args[0]
            else:
                raise ValueError(
                    "You need to pass an Element class to Style.set_as_default(), "
                    "or typehint Style for an element."
                )
        _c.default_styles[cls] = self
        return self

    def process_event(self, element: "Style", event: pygame.event.Event) -> None:
        super().process_event(element, event)
        for state in self.states:
            state.process_event(element, event)

    def activate(self, element: T, event: Optional[pygame.Event] = None) -> None:
        log.style.line_break()
        with log.style.indent(f"Activated for {element}...", self):
            if self.active_callable is not None:
                self.active_callable(element, event)

            self._on_become_active(element, event)

            for state in self.states:
                if state.active_by_default:
                    state.activate(element, event)

    def deactivate(self, element: T, event: Optional[pygame.Event] = None) -> None:
        log.style.line_break()
        with log.style.indent(f"Deactivated for {element}...", self):
            if self.deactive_callable is not None:
                self.deactive_callable(element, event)
            self._on_become_deactive(element, event)

            for state in self.states:
                state.deactivate(element, event)

    def on_become_active(self, func: ListenerCallable) -> ListenerCallable:
        self.active_callable = func
        return func

    def on_become_deactive(self, func: ListenerCallable) -> ListenerCallable:
        self.deactive_callable = func
        return func

    def _on_become_active(self, element: T, event: Optional[pygame.Event]) -> None:
        ...

    def _on_become_deactive(self, element: T, event: Optional[pygame.Event]) -> None:
        ...
