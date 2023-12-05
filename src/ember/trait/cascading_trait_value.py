from typing import Generic, TypeVar, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ember.trait.bound_trait import TraitReference
    from ember.ui.element import Element

T = TypeVar("T")


class CascadingTraitValue(Generic[T]):
    context_depth: int = 0
    new_elements: list["Element"] = []

    def __init__(
        self, ref: Optional["TraitReference"], value: Optional[T], depth: Optional[int] = 1
    ) -> None:
        self.ref: Optional["TraitReference"] = ref
        self.value: Optional[T] = value
        self.depth: Optional[int] = depth

    def prepare_for_descent(self, instance: "Element") -> None:
        ...

    def __enter__(self):
        CascadingTraitValue.context_depth += 1

    def __exit__(self, exc_type, exc_val, exc_tb):

        for element in CascadingTraitValue.new_elements:
            if element.parent is not None:
                continue

            if isinstance(element, self.ref.owner):
                context = self.ref.trait.get_context(element)
                if context.element_value is None:
                    context.set_value(self.value)

        CascadingTraitValue.context_depth -= 1
        if CascadingTraitValue.context_depth == 0:
            CascadingTraitValue.new_elements.clear()

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
