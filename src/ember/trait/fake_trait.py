from typing import TypeVar, Callable, Optional

from ember.base.element import Element
from .base_trait import BaseTrait
from .trait import Trait, TraitReference
from .cascading_trait_value import CascadingTraitValue

T = TypeVar("T")


def FakeTrait(
    posing_as: Trait
) -> Callable[[Callable[[Element], Trait]], "_ConditionalTrait"]:
    def decorator(func: Callable[[Element], Trait]) -> "_ConditionalTrait":
        return _ConditionalTrait(func, posing_as)

    return decorator


class _ConditionalTrait(BaseTrait[T]):
    def __init__(self, func: Callable[[Element], Trait], posing_as: Trait) -> None:
        self.func: Callable[[Element], Trait] = func
        self.posing_as: Trait = posing_as

    def __get__(self, instance, owner):
        BaseTrait.inspected_class = owner
        if instance is None:
            return self
        return getattr(instance, self.func(instance).name)

    def __set__(self, instance, value) -> None:
        setattr(instance, self.func(instance).name, value)

    def __call__(
        self, value: T, depth: Optional[int] = None
    ) -> CascadingTraitValue[T]:
        ref = TraitReference(trait=self.posing_as, owner=BaseTrait.inspected_class)
        return CascadingTraitValue(ref=ref, value=value, depth=depth or self.posing_as.default_cascade_depth)

