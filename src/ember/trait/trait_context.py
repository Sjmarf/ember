from typing import TypeVar, Generic, Optional, TYPE_CHECKING, Union

from ..animation import Animation
from .trait_layer import TraitLayer

from .trait import Trait
if TYPE_CHECKING:
    from .trait_value import TraitValue
    from ..base.element import Element

T = TypeVar("T")


class TraitContext(Generic[T]):
    __slots__ = (
        "_element",
        "trait_value",
        "value",
        "animation_value",
        "element_value",
        "parent_value",
        "_children",
    )

    def __init__(self, element: "Element", trait_value: "TraitValue") -> None:
        self._element: "Element" = element
        self.trait_value: TraitValue = trait_value

        trait = getattr(self._element, self.trait_value.trait_name)
        self.value: Optional[T] = trait._default_value

        self.animation_value: Union[T, "TraitValue", None] = None
        self.element_value: Union[T, "TraitValue", None] = None
        self.parent_value: Union[T, "TraitValue", None] = None

        self._children: list["TraitContext"] = []

    def __repr__(self) -> str:
        return (
            f"<TraitContext(value={self.value}, "
            f"animation_value={self.animation_value}, "
            f"element_value={self.element_value}, "
            f"parent_value={self.parent_value})>"
        )

    def __getitem__(self, item: TraitLayer) -> Union[T, "TraitValue", None]:
        if item == TraitLayer.ELEMENT:
            return self.element_value
        if item == TraitLayer.PARENT:
            return self.parent_value
        return self.animation_value

    def set_value(
        self,
        value: Union[T, "Trait", None],
    ) -> bool:

        if not Trait.inspected_layer == TraitLayer.DEFAULT:
            current_value = self[Trait.inspected_layer]
            if current_value == value:
                return False

            if isinstance(current_value, TraitContext):
                current_value._children.remove(self)

            if isinstance(value, TraitContext):
                value._children.append(self)

            if Trait.inspected_layer == TraitLayer.ELEMENT:
                self.element_value = value
            elif Trait.inspected_layer == TraitLayer.PARENT:
                self.parent_value = value
            else:
                self.animation_value = value

        old_val = self.value
        needs_update = self.update()

        if hasattr(self._element, "_animation_contexts"):
            for c in self._element._animation_contexts[:]:
                if c.trait_context is self:
                    c._finish()
                    self._element._animation_contexts.remove(c)
                    self.update()
                    break

            if (anim := Animation.animation_stack[-1]) is not None:
                context = anim.create_context(self, old_val, self.value)

                self._element._animation_contexts.append(context)
                val = context.target._get_value(context)
                self.animation_value = val
                self.value = val
                for child in self._children:
                    child.update()

        if getattr(self._element, "_has_built", False) and needs_update:
            self.send_callbacks()
        return True

    def update(self) -> bool:
        trait = getattr(self._element, self.trait_value.trait_name)
        for i in (self.animation_value, self.element_value, self.parent_value, trait._default_value):
            if i is not None:
                if isinstance(i, TraitContext):
                    i = i.value
                    if i is None:
                        continue
                if i != self.value:
                    self.value = i
                    return True
                return False

        if self.value is None:
            return False
        self.value = None
        return True

    def send_callbacks(self) -> None:
        trait = getattr(self._element, self.trait_value.trait_name)
        if self._element._has_built:
            for call in trait.on_update:
                call(self._element)

            for child in self._children:
                child.update()
                child.send_callbacks()
