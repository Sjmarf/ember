import abc
import itertools

from typing import Union, TYPE_CHECKING, Optional, Sequence, Callable, Iterable, Type
from ember import log

from ..on_event import queue as on_event_queue

if TYPE_CHECKING:
    from .element import Element

EmptyCallable = Callable[[], None]
MethodCallable = Callable[["Element"], None]


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
