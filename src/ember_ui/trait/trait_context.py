from typing import TypeVar, Generic, Optional, TYPE_CHECKING, Union

from ..animation import Animation
from .trait_layer import TraitLayer
from . import trait_layer

if TYPE_CHECKING:
    from .trait_value import TraitValue
    from .trait import Trait
    from ember_ui.ui.element import Element

T = TypeVar("T")


class TraitContext(Generic[T]):
    __slots__ = (
        "__weakref__",
        "_element",
        "trait",
        "value",
        "animation_value",
        "element_value",
        "parent_value",
        "_children",
    )

    def __init__(self, element: "Element", trait: "Trait") -> None:
        self._element: "Element" = element
        self.trait: "Trait" = trait

        self.value: Optional[T] = trait._default_value
        if self.value is not None:
            trait.activate_value(self.value, self._element)

        self.animation_value: Union[T, "TraitValue", None] = None
        self.element_value: Union[T, "TraitValue", None] = None
        self.parent_value: Union[T, "TraitValue", None] = None

        self._children: list["TraitContext"] = []

    def __repr__(self) -> str:
        return (
            f"<TraitContext(value={self.value}, "
            f"animation={self.animation_value}, "
            f"element={self.element_value}, "
            f"parent={self.parent_value}, "
            f"default={self.trait._default_value})>"
        )

    def __getitem__(self, item: TraitLayer) -> Union[T, "TraitValue", None]:
        if item == TraitLayer.ELEMENT:
            return self.element_value
        if item == TraitLayer.PARENT:
            return self.parent_value
        return self.animation_value
    
    def __setitem__(self, layer: TraitLayer, value: Union[T, "TraitValue", None]) -> None:
        if layer == TraitLayer.ELEMENT:
            self.element_value = value
        elif layer == TraitLayer.PARENT:
            self.parent_value = value
        else:
            self.animation_value = value        
    
    def update_existing_value(self, old_value: Union[T, "Trait", None], new_value: Union[T, "Trait", None]) -> None:
        if self.value is new_value:
            self.value = old_value
            self.set_value(new_value)

    def set_value(
        self,
        value: Union[T, "Trait", None],
    ) -> bool:
        if not trait_layer.inspected == TraitLayer.DEFAULT:
            current_value = self[trait_layer.inspected]
            
            #if current_value is value:
                #return False

            if isinstance(current_value, TraitContext):
                current_value._children.remove(self)

            if isinstance(value, TraitContext):
                value._children.append(self)
            
            self[trait_layer.inspected] = value

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
        for i in (self.animation_value, self.element_value, self.parent_value, self.trait._default_value):
            if i is not None:
                if isinstance(i, TraitContext):
                    i = i.value
                    if i is None:
                        continue
                if i is not self.value:
                    if self.value is not None:
                        self.trait.deactivate_value(self.value, self)
                    self.value = i
                    if i is not None:
                        self.trait.activate_value(self.value, self)
                    return True
                return False

        if self.value is None:
            return False
        self.value = None
        return True

    def send_callbacks(self) -> None:
        if self._element._has_built:
            for call in self.trait.on_update:
                call(self._element)

            for child in self._children:
                child.update()
                child.send_callbacks()
