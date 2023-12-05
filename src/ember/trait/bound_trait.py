from typing import Type, TYPE_CHECKING, TypeVar, Optional, NamedTuple

from .cascading_trait_value import CascadingTraitValue

if TYPE_CHECKING:
    from .trait import Trait
    from ..ui.element import Element

T = TypeVar("T")


class BoundTrait:
    __slots__ = ("trait", "owner")

    def __init__(self, trait: "Trait[T]", owner: Type["Element"]) -> None:
        self.trait: "Trait" = trait
        self.owner: Type["Element"] = owner

    def __call__(self, value: T, depth: Optional[int] = None) -> CascadingTraitValue[T]:
        return CascadingTraitValue(
            self.create_reference(),
            self.trait.load_value(value),
            depth=(depth or self.trait.default_cascade_depth),
        )

    def create_reference(self) -> "TraitReference":
        # TODO: Can we replace TraitReference with BoundTrait entirely? They both have the same attrs
        return TraitReference(trait=self.trait, owner=self.owner)

    @property
    def default_value(self) -> T:
        return self.trait.get_default_value(self.owner)

    @default_value.setter
    def default_value(self, value: T) -> None:
        self.trait.set_default_value(self.owner, value)


class TraitReference(NamedTuple):
    trait: "Trait"
    owner: Type["Element"]
