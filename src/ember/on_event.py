from typing import Callable

EmptyCallable = Callable[[], None]

queue: list[tuple[EmptyCallable, tuple[int]]] = []
def on_event(*event_types: int):
    def decorator(func: EmptyCallable):
        queue.append((func, event_types))
        return func

    return decorator
