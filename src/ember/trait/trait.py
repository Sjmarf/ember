from typing import (
    TypeVar,
    Generic,
    TYPE_CHECKING,
    Optional,
    Any,
    Callable,
    Union,
    Type,
    Self,
)
from contextlib import contextmanager
from weakref import WeakSet

if TYPE_CHECKING:
    from ember.base.element import Element
    from .trait_context import TraitContext

from .trait_layer import TraitLayer
from .. import log

T = TypeVar("T")


class Trait(Generic[T]):
    inspected_layer: TraitLayer = TraitLayer.ELEMENT
    Layer = TraitLayer

    def __init__(
        self,
        default_value: T,
        on_update: Union[
            Callable[["Element"], Any], tuple[Callable[["Element"], Any], ...]
        ] = (),
    ) -> None:
        self._default_value: T = default_value
        self.on_update: tuple[Callable[["Element"], Any], ...] = (
            on_update if isinstance(on_update, tuple) else (on_update,)
        )

        self.owner: Optional[Type["Element"]] = None
        self.name: Optional[str] = None
        self.context_name: Optional[str] = None

        self._defaulted_elements: WeakSet["Element"] = WeakSet()

    def __get__(self, instance, owner) -> Self:
        return self

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name[:-1]
        self.context_name = f"_{name[:-1]}"
        log.trait.info(f"Created {self.owner.__name__}.{self.name}")

    @property
    def default_value(self) -> T:
        return self._default_value

    @default_value.setter
    def default_value(self, value: T) -> None:
        if value != self._default_value:
            log.trait.info(f"Updated default size for {self.owner.__name__}.{self.name}")
            self._default_value = value
            for element in self._defaulted_elements:
                context: "TraitContext" = getattr(element, self.context_name, None)
                with self.inspecting(TraitLayer.DEFAULT):
                    context.set_value(value)

    @classmethod
    @contextmanager
    def inspecting(cls, layer: TraitLayer) -> None:
        prev_value = cls.inspected_layer
        cls.inspected_layer = layer
        yield
        cls.inspected_layer = prev_value

    def copy(self, default_value: Optional[T]) -> "Trait":
        new = Trait(
            default_value=default_value
            if default_value is not None
            else self.default_value,
            on_update=self.on_update,
        )
        new._defaulted_elements = self._defaulted_elements

        return new
