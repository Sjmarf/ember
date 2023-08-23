from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ember.trait.trait_context import TraitContext

from .animation_context import AnimationContext, SimpleAnimationContext


class Animation(ABC):
    animation_stack: list[Optional["Animation"]] = [None]

    def __enter__(self):
        self.animation_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.animation_stack.pop()

    def create_context(
        self, trait_context: "TraitContext", old_value: Any, new_value: Any
    ) -> AnimationContext:
        return AnimationContext(self, trait_context, old_value, new_value)

    @abstractmethod
    def _update(self, context: "AnimationContext") -> bool:
        pass

class SimpleAnimation(Animation, ABC):
    def __init__(self, duration: float) -> None:
        self.duration: float = duration

    def create_context(
        self, trait_context: "TraitContext", old_value: Any, new_value: Any
    ) -> SimpleAnimationContext:
        return SimpleAnimationContext(self, trait_context, old_value, new_value)

class AnimationEscaping:
    def __enter__(self):
        Animation.animation_stack.append(None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        Animation.animation_stack.pop()


ESCAPING = AnimationEscaping()
