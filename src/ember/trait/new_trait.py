from typing import TypeVar, Union, Any, Callable, TYPE_CHECKING

from .trait_value import TraitValue
from .trait import Trait

if TYPE_CHECKING:
    from ..base.element import Element

T = TypeVar("T")

ElementCallable = Callable[["Element"], Any]
