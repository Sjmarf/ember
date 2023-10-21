from typing import TypeVar, Optional, Union, Callable, Any, TYPE_CHECKING

from .trait import Trait
from .conditional_cascading_trait_value import ConditionalCascadingTraitValue

if TYPE_CHECKING:
    from ember.base.element import Element

T = TypeVar("T")


class ReplacementTrait(Trait[T]):
    def __init__(
        self,
        default_value: Optional[T],
        on_call: Callable,
        on_update: Union[
            Callable[["Element"], Any], tuple[Callable[["Element"], Any], ...]
        ] = (),
        load_value_with: Optional[Callable] = None,
        default_cascade_depth: int = -1,
    ):
        self.on_call: Callable = on_call
        super().__init__(
            default_value=default_value,
            on_update=on_update,
            load_value_with=load_value_with,
            default_cascade_depth=default_cascade_depth,
        )

    def __call__(
        self, value: T, depth: Optional[int] = None, owner=None,
    ) -> ConditionalCascadingTraitValue[T]:
        if owner is None:
            return super().__call__(value, depth)
        return ConditionalCascadingTraitValue(
            func=self.on_call, owner=owner, input_value=value, input_depth=depth
        )

    def copy(self, default_value: Optional[T]) -> "ReplacementTrait":
        new = type(self)(
            default_value=default_value
            if default_value is not None
            else self.default_value,
            on_update=self.on_update,
            load_value_with=self.load_value_with,
            on_call=self.on_call,
        )
        new.context_name = self.context_name
        new._defaulted_elements = self._defaulted_elements

        return new
