from typing import (
    TypeVar,
    TYPE_CHECKING,
    Optional,
    Any,
    Callable,
    Union,
    Type,
)

if TYPE_CHECKING:
    from ember.ui.element import Element

from . import trait_layer
from .trait_layer import TraitLayer
from .trait_context import TraitContext
from .trait_dependency import TraitDependency
from .bound_trait import BoundTrait
from .cascading_trait_value import CascadingTraitValue
from .. import log
from .base_trait import BaseTrait

T = TypeVar("T")


class Trait(BaseTrait[T]):
    Layer = TraitLayer

    def __init__(
        self,
        default_value: Optional[T],
        on_update: Union[
            Callable[["Element"], Any], tuple[Callable[["Element"], Any], ...]
        ] = (),
        load_value_with: Optional[Callable] = None,
        default_cascade_depth: int = -1,
    ) -> None:
        self.owner: Optional[Type["Element"]] = None
        self.name: Optional[str] = None
        self.context_name: Optional[str] = None
        self.default_name: Optional[str] = None

        self.load_value_with: Optional[Callable] = load_value_with

        self._default_value: T = self.load_value(default_value)
        """
        Temporary variable to store the default value until __set_name__ is called,
        at which point the default is set within the attached class and this attribute is
        deleted.
        """

        self.on_update: tuple[Callable[["Element"], Any], ...] = (
            on_update if isinstance(on_update, tuple) else (on_update,)
        )
        self.default_cascade_depth: int = default_cascade_depth

    def __repr__(self) -> str:
        return f"<Trait('{self.name}')>"

    def __get__(self, instance: "Element", owner: Type["Element"]) -> T | BoundTrait:
        # We can't just use the 'element_type' instance attr for this because of inheritance
        if instance is None:
            return BoundTrait(self, owner)
        context = getattr(instance, self.context_name, None)
        if context is None:
            context = TraitContext(instance, self)
            setattr(instance, self.context_name, context)
        return context.value

    def get_context(self, element: "Element") -> TraitContext[T]:
        if not isinstance(element, self.owner):
            raise ValueError(f"Element does not inherit from {self.owner}.")

        return getattr(element, self.context_name)

    def __set__(self, instance: "Element", value: T) -> None:
        value = self.load_value(value)

        log.trait.info(
            f"Setting {instance.__class__.__name__}.{self.context_name} value to {value}"
        )
        context: TraitContext = getattr(instance, self.context_name, None)

        if context is None:
            context = TraitContext(instance, self)
            setattr(instance, self.context_name, context)

        context.set_value(value)

    def __set_name__(self, owner, name) -> None:
        self.owner = owner
        self.name = name
        self.context_name = f"_{name}"
        self.default_name = f"_{name}_default"
        setattr(owner, self.default_name, self._default_value)
        del self._default_value
        log.trait.info(f"Created {self.owner.__name__}.{self.name}")

    def load_value(self, value: T) -> T:
        if self.load_value_with is not None:
            new_value = self.load_value_with(value)
            return new_value
        return value

    def get_default_value(self, owner: Type["Element"]) -> T:
        return getattr(owner, self.default_name)

    def set_default_value(self, owner: Type["Element"], value: T) -> None:
        if not issubclass(owner, self.owner):
            raise ValueError(f"{owner} is not a subclass of {self.owner}.")

        value = self.load_value(value)
        if value is not self.get_default_value(owner):
            log.trait.info(
                f"Updated default value for {owner.__name__}.{self.name}"
            )

            setattr(owner, self.default_name, value)

    def activate_value(self, value: T, context: "TraitContext") -> None:
        """
        Called when a value of the Trait becomes active.
        """
        if isinstance(value, TraitDependency):
            value.trait_contexts.add(context)

    def deactivate_value(self, value: T, context: "TraitContext") -> None:
        """
        Called when a value of the Trait becomes deactive.
        """
        if isinstance(value, TraitDependency) and context in value.trait_contexts:
            value.trait_contexts.remove(context)
