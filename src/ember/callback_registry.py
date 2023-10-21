import copy
from typing import Union, TYPE_CHECKING, Optional, Sequence, Callable, Iterable, Type

if TYPE_CHECKING:
    from ember.base.element import Element

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