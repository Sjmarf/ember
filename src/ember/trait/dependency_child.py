from contextlib import nullcontext
from typing import Generic, TypeVar, TYPE_CHECKING, Callable

from .trait_dependency import TraitDependency


GetType = TypeVar("GetType", bound=TraitDependency | None)
SetType = TypeVar("SetType", bound=TraitDependency | None)

class DependencyChild(Generic[GetType, SetType]):
    
    def __init__(self, load_value_with: Callable[[SetType], GetType] | None) -> None:
        self.load_value_with: Callable[[SetType], GetType] | None = load_value_with
        self._value_name: str | None = None
    
    def __set_name__(self, owner: type[TraitDependency], name: str) -> None:
        self._value_name = f"_{name}"
    
    def __get__(self, instance: TraitDependency, owner: type[TraitDependency]) -> GetType:
        return getattr(instance, self._value_name) 
       
    def __set__(self, instance: TraitDependency, value: SetType) -> None:
        if self.load_value_with is not None:
            value = self.load_value_with(value)
        
        old_value = getattr(instance, self._value_name, -1)
        
        if value != old_value:      
            with nullcontext() if old_value == -1 else instance.trait_update():
                setattr(instance, self._value_name, value)
                if isinstance(old_value, TraitDependency) and instance in old_value._parent_dependencies:
                    old_value._parent_dependencies.remove(instance)
                setattr(instance, self._value_name, value)
                if isinstance(value, TraitDependency):
                    value._parent_dependencies.add(instance)
        else:
            setattr(instance, self._value_name, value)
