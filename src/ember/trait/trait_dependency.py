from typing import Union, Sequence, Optional, TYPE_CHECKING, Callable, ParamSpec, Self, Generator
from contextlib import contextmanager
from abc import ABC, abstractmethod
from weakref import WeakSet

from ember import log

if TYPE_CHECKING:
    from ember.trait.trait_context import TraitContext
    
P = ParamSpec("P")

class TraitDependency(ABC):
    def __init__(self) -> None:
        self.trait_contexts: WeakSet[TraitContext] = WeakSet()
        self._parent_dependencies: WeakSet[TraitDependency] = WeakSet()
        
    def child_updated(self):
        ...
        
    @classmethod
    def triggers_trait_update(cls, func: Callable[P, None]) -> None:
        def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> None:
            with self.trait_update():
                func(self, *args, **kwargs)
        return wrapper
    
    @contextmanager
    def trait_update(self):
        with log.size.indent("Value was updated, triggering trait update...", self):
            gen = self.trait_update_chain()
            next(gen)
            log.size.info("Updating value...", self)
            yield
            next(gen)
    
    def trait_update_chain(self) -> Generator[None, None, None]:
        log.size.info("Copy made...", self)
        old_value = self.copy()
        parents = [i.trait_update_chain() for i in self._parent_dependencies]
        [next(i) for i in parents]
        yield
        self.child_updated()
        for context in self.trait_contexts:
            log.size.info(f"Updating TraitContext for {context._element}...", self)
            context.update_existing_value(old_value, self)
        [next(i) for i in parents]
        yield

    @abstractmethod
    def copy(self) -> "TraitDependency":
        ...
    
