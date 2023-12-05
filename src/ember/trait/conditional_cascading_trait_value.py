from typing import Callable, TYPE_CHECKING, TypeVar, Type

if TYPE_CHECKING:
    from ember.ui.element import Element

from .trait import Trait
from .bound_trait import TraitReference
from .cascading_trait_value import CascadingTraitValue
from ember import log

T = TypeVar("T")


class ConditionalCascadingTraitValue(CascadingTraitValue[T]):
    def __init__(
        self, func: Callable[["Element"], Trait], owner: Type["Element"], input_value: T, input_depth: int = 1
    ) -> None:
        self.func: Callable[[Element], Trait] = func
        self.owner: Type["Element"] = owner
        self.input_value: T = input_value
        self.input_depth: int = input_depth
        super().__init__(None, None, None)

    def prepare_for_descent(self, instance: "Element") -> None:
        trait = self.func(instance)
        self.ref = TraitReference(trait=trait, owner=self.owner)
        log.cascade.info(f"Acting as {self.ref}...")
        self.value = trait.load_value(self.input_value)
        self.depth = (self.input_depth or trait.default_cascade_depth)

