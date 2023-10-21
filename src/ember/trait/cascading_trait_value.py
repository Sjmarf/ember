from typing import Generic, TypeVar, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ember.trait.trait import Trait, TraitReference
    from ember.base.element import Element

T = TypeVar("T")


class CascadingTraitValue(Generic[T]):
    def __init__(
        self, ref: Optional["TraitReference"], value: Optional[T], depth: Optional[int] = 1
    ) -> None:
        self.ref: Optional["TraitReference"] = ref
        self.value: Optional[T] = value
        self.depth: Optional[int] = depth

    def prepare_for_descent(self, instance: "Element") -> None:
        ...

    def __repr__(self) -> str:
        if self.ref is None:
            return f"<CascadingTraitValue(Values undecided)>"
        return f"<CascadingTraitValue(ref='{self.ref}', value={self.value}, depth={self.depth})>"

    def __add__(self, other):
        return CascadingTraitValue(self.ref, self.value + other, self.depth)

    def __sub__(self, other):
        return CascadingTraitValue(self.ref, self.value - other, self.depth)

    def __mul__(self, other):
        return CascadingTraitValue(self.ref, self.value * other, self.depth)

    def __truediv__(self, other):
        return CascadingTraitValue(self.ref, self.value / other, self.depth)
