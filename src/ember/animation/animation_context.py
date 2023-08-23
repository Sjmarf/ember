from typing import Any, TYPE_CHECKING
from .animated_value import (
    AnimatedValue,
    AnimatedSizeValue,
    AnimatedPositionValue,
    AnimatedSpacingValue,
)
from ..size import Size
from ember.position.position import Position
from ..spacing import Spacing
from .. import common as _c


if TYPE_CHECKING:
    from ember.trait.trait import TraitContext
    from .animation import Animation
class AnimationContext:
    def __init__(
        self, anim: "Animation", trait_context: "TraitContext", old_value: Any, new_value: Any
    ) -> None:
        self.anim: "Animation" = anim
        self.trait_context: "TraitContext" = trait_context

        self.value: float = 0

        self.target: AnimatedValue

        if isinstance(new_value, Size):
            self.target = AnimatedSizeValue(old_value, new_value)
        elif isinstance(new_value, Position):
            self.target = AnimatedPositionValue(old_value, new_value)
        elif isinstance(new_value, Spacing):
            self.target = AnimatedSpacingValue(old_value, new_value)
        else:
            raise _c.Error("Animating this datatype is not supported.")

    def _update(self) -> bool:
        val = self.target._get_value(self)
        self.trait_context.animation_value = val
        self.trait_context.update()
        self.trait_context.send_callbacks()
        return self.anim._update(self)

    def _finish(self) -> None:
        self.trait_context.animation_value = None
        self.trait_context.update()
        self.trait_context.send_callbacks()

class SimpleAnimationContext(AnimationContext):
    def __init__(
        self, anim: "Animation", trait_context: "TraitContext", old_value: Any, new_value: Any
    ) -> None:
        super().__init__(anim, trait_context, old_value, new_value)
        self.progress: float = 0
