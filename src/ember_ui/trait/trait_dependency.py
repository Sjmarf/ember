from typing import Union, Sequence, Optional, TYPE_CHECKING, Callable, ParamSpec, Self, Generator
from contextlib import contextmanager
from abc import ABC, abstractmethod
from weakref import WeakSet

from ember_ui import log

if TYPE_CHECKING:
    from ember_ui.trait.trait_context import TraitContext
    
P = ParamSpec("P")

class TraitDependency(ABC):
    def __init__(self) -> None:
        self.trait_contexts: WeakSet[TraitContext] = WeakSet()
        self._parent_dependencies: WeakSet[TraitDependency] = WeakSet()
        
    @classmethod
    def triggers_trait_update(cls, func: Callable[P, None]) -> None:
        def wrapper(self, *args: P.args) -> None:
            with log.size.indent("Value was updated, triggering trait update...", self):
                gen = self.trait_update_chain()
                next(gen)
                log.size.info("Updating value...", self)
                func(self, *args)
                next(gen)
        return wrapper
    
    def trait_update_chain(self) -> Generator[None, None, None]:
        log.size.info("Copy made...", self)
        old_value = self.copy()
        parents = [i.trait_update_chain() for i in self._parent_dependencies]
        [next(i) for i in parents]
        yield
        for context in self.trait_contexts:
            log.size.info(f"Updating TraitContext for {context._element}...", self)
            context.update_existing_value(old_value, self)
        [next(i) for i in parents]
        yield
    
    @abstractmethod
    def copy(self) -> "TraitDependency":
        ...