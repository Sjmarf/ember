from typing import Any, TYPE_CHECKING, Generator
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
    """
    Represents an in-progress animation. There is an AnimationContext for each trait of an element currently being animated.
    An element's AnimationContexts are stored in the 'animations' attributes of the element.
    """
    
    def __init__(
        self,
        anim: "Animation",
        trait_context: "TraitContext",
        old_value: Any,
        new_value: Any,
    ) -> None:
        self.anim_gen: Generator[float, None, None] = anim.steps()
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
            raise _c.Error(
                f"Animating the datatype '{type(new_value).__name__}' is not supported. old_value={old_value}, new_value={new_value}"
            )

    def _update(self) -> bool:
        """
        Returns True when the animation has finished.
        """
        val = self.target._get_value(self)
        self.trait_context.animation_value = val
        self.trait_context.update()
        self.trait_context.send_callbacks()
        try:
            self.value = next(self.anim_gen)
            return False
        except StopIteration:
            return True

    def _finish(self) -> None:
        self.trait_context.animation_value = None
        self.trait_context.update()
        self.trait_context.send_callbacks()
