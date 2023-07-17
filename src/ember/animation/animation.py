from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING, Optional
from .animated_value import AnimatedValue, AnimatedSizeValue, AnimatedPositionValue
from ..size import Size
from ..position import Position


if TYPE_CHECKING:
    from ..ui.base.element import Element


class AnimationContext:
    def __init__(
        self,
        element: "Element",
        anim: "Animation",
        func: callable,
        values: dict[str, Any],
    ) -> None:
        self.element: "Element" = element
        self.anim: "Animation" = anim
        self.func: callable = func
        
        self.progress: float = 0
        
        self.values: dict[str, AnimatedValue] = {}
        
        for key, (old_value, new_value) in values.items():
            if isinstance(new_value, Size):
                self.values[key] = AnimatedSizeValue(old_value, new_value)
            elif isinstance(new_value, Position):
                self.values[key] = AnimatedPositionValue(old_value, new_value)

    def _update(self) -> bool:
        return self.anim._update(self)
    
    def _finish(self):
        return self.anim._finish(self)


class Animation(ABC):
    animation_stack: list[Optional["Animation"]] = [None]

    def __init__(self):
        pass

    def __enter__(self):
        self.animation_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.animation_stack.pop()

    @abstractmethod
    def create_context(
        self, element: "Element", func: callable, values: dict[str, Any]
    ) -> AnimationContext:
        pass

    @abstractmethod
    def _update(self, context: AnimationContext) -> bool:
        pass
    
    def _finish(self, context: AnimationContext) -> None:
        pass


class AnimationEscaping:
    def __enter__(self):
        Animation.animation_stack.append(None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        Animation.animation_stack.pop()


ESCAPING = AnimationEscaping()
