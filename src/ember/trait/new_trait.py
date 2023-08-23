from typing import TypeVar, Union, Any, Callable, TYPE_CHECKING

from .trait_value import TraitValue
from .trait import Trait

if TYPE_CHECKING:
    from ..base.element import Element

T = TypeVar("T")

ElementCallable = Callable[["Element"], Any]


def new_trait(
    default_value: T,
    on_update: Union[ElementCallable, tuple[ElementCallable, ...]] = (),
) -> tuple[TraitValue[T], Trait[T]]:

    trait = Trait(default_value, on_update=on_update)
    value = TraitValue()

    return value, trait
