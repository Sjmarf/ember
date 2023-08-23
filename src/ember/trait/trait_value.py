from typing import Optional, Generic, TypeVar, TYPE_CHECKING, Type

from .trait_context import TraitContext

T = TypeVar("T")

if TYPE_CHECKING:
    from ..base.element import Element


class TraitValue(Generic[T]):
    __slots__ = ("trait", "context_name", "trait_name")

    def __init__(self) -> None:
        self.context_name: Optional[str] = None

    def __repr__(self) -> str:
        return f"<TraitValue({self.context_name[1:] if self.context_name else 'None'})>"

    def __set_name__(self, element_type: Type["Element"], name) -> None:
        element_type._trait_values += (self,)
        self.context_name = f"_{name}"
        self.trait_name = f"{name}_"

    def __get__(self, element: "Element", element_type: Type["Element"]) -> T:
        return getattr(element, self.context_name).value

    def __set__(self, element: "Element", value: T) -> None:
        context: TraitContext = getattr(element, self.context_name, None)

        if context is None:
            context = TraitContext(element, self)
            setattr(element, self.context_name, context)

        trait = getattr(element, self.trait_name)
        context.set_value(value)

        if context.value is trait._default_value:
            trait._defaulted_elements.add(element)
        else:
            if element in trait._defaulted_elements:
                trait._defaulted_elements.remove(element)
