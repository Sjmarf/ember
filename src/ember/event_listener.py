import pygame
from typing import Callable, Optional, TYPE_CHECKING, Generator, Generic, TypeVar

if TYPE_CHECKING:
    from ember.ui.base.mixin.style import Style


T = TypeVar("T", bound="Style", covariant=True)

ListenerCallable = Callable[[T, Optional[pygame.Event]], None]

class EventListener(Generic[T]):
    def __init__(self, *args, **kwargs) -> None:
        self.event_calls: dict[int, list[ListenerCallable]] = {}
        super().__init__(*args, **kwargs)

    def process_event(self, element: "Style", event: pygame.event.Event) -> None:
        if event.type in self.event_calls:
            for call in self.event_calls[event.type]:
                call(element, event)

    def on_event(self, event_type: int) -> callable:
        def decorator(func: callable) -> callable:
            self.add_event_callback(func, event_type)
            return func

        return decorator

    def add_event_callback(self, func: ListenerCallable, event_type: int) -> None:
        if event_type not in self.event_calls:
            self.event_calls[event_type] = []
        self.event_calls[event_type].append(func)
