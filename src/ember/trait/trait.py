from typing import (
    TypeVar,
    TYPE_CHECKING,
    Optional,
    Any,
    Callable,
    Union,
    Type,
    NamedTuple
)
from weakref import WeakSet

if TYPE_CHECKING:
    from ember.ui.element import Element

from .trait_layer import TraitLayer
from .trait_context import TraitContext
from .trait_dependency import TraitDependency
from .cascading_trait_value import CascadingTraitValue
from .. import log
from .base_trait import BaseTrait

T = TypeVar("T")

class TraitReference(NamedTuple):
    trait: "Trait"
    owner: Type["Element"]


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

        self.load_value_with: Optional[Callable] = load_value_with
        self._default_value: T = self.load_value(default_value)
        self.on_update: tuple[Callable[["Element"], Any], ...] = (
            on_update if isinstance(on_update, tuple) else (on_update,)
        )
        self.default_cascade_depth: int = default_cascade_depth

        self._defaulted_elements: WeakSet["Element"] = WeakSet()

    def __repr__(self) -> str:
        return f"<Trait('{self.name}')>"

    def __get__(self, instance: "Element", owner: Type["Element"]) -> T:
        # We can't just use the 'element_type' instance attr for this because of inheritance
        BaseTrait.inspected_class = owner
        if instance is None:
            return self
        context = getattr(instance, self.context_name, None)
        if context is None:
            context = TraitContext(instance, self)
            setattr(instance, self.context_name, context)            
        return context.value

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

        if context.value is self._default_value:
            self._defaulted_elements.add(instance)
        else:
            if instance in self._defaulted_elements:
                self._defaulted_elements.remove(instance)

    def __set_name__(self, owner, name) -> None:
        self.owner = owner
        self.name = name
        self.context_name = f"_{name}"
        log.trait.info(f"Created {self.owner.__name__}.{self.name}")

    def __call__(self, value: T, depth: Optional[int] = None) -> CascadingTraitValue[T]:
        return CascadingTraitValue(
            self.create_reference(), self.load_value(value), depth=(depth or self.default_cascade_depth)
        )

    def load_value(self, value: T) -> T:
        if self.load_value_with is not None:
            new_value = self.load_value_with(value)
            return new_value
        return value
    
    def create_reference(self) -> TraitReference:
        return TraitReference(trait=self, owner=BaseTrait.inspected_class)

    @property
    def default_value(self) -> T:
        return self._default_value

    @default_value.setter
    def default_value(self, value: T) -> None:
        value = self.load_value(value)
        if value is not self._default_value:
            log.trait.info(
                f"Updated default value for {Trait.inspected_class.__name__}.{self.name}"
            )

            new_trait = self.copy(value)
            new_trait.name = self.name
            setattr(Trait.inspected_class, self.name, new_trait)

            for element in self._defaulted_elements:
                context: "TraitContext" = getattr(element, self.context_name, None)
                with self.inspecting(TraitLayer.DEFAULT):
                    context.set_value(new_trait._default_value)

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

    def copy(self, default_value: Optional[T]) -> "Trait":
        new = type(self)(
            default_value=default_value
            if default_value is not None
            else self.default_value,
            on_update=self.on_update,
            load_value_with=self.load_value_with
        )
        new.owner = self.owner
        new.name = self.name
        new.context_name = self.context_name
        new._defaulted_elements = self._defaulted_elements

        return new
