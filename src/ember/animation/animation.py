from abc import ABC, abstractmethod
import copy
from typing import Any, TYPE_CHECKING, Optional, Generator

if TYPE_CHECKING:
    from ember.trait.trait_context import TraitContext

from .animation_context import AnimationContext


class Animation(ABC):
    animation_stack: list[Optional["Animation"]] = [None]
    
    def __init__(self, weak: bool = False) -> None:
        self.weak: bool = weak
        
    def __enter__(self):
        if (not self.weak) or self.animation_stack[-1] is None:
            self.animation_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.animation_stack[-1] is self:
            self.animation_stack.pop()
        
    def as_weak(self) -> "Animation":
        """
        Create a copy of the Animation and set the 'weak' attribute of the copy to True.
        """
        new = copy.copy(self)
        new.weak = True
        return new

    @abstractmethod
    def steps(self) -> Generator[float, None, None]:
        ...


class AnimationEscaping:
    def __enter__(self):
        Animation.animation_stack.append(None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        Animation.animation_stack.pop()


ESCAPING = AnimationEscaping()
