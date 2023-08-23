from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from ..size import Size, InterpolatedSize
from ember.position import Position, InterpolatedPosition
from ..spacing import Spacing, InterpolatedSpacing

if TYPE_CHECKING:
    from .animation import AnimationContext


class AnimatedValue(ABC):
    def __init__(self, old_value, new_value) -> None:
        self.old_value = old_value
        self.new_value = new_value

    @abstractmethod
    def _get_value(self, context: "AnimationContext") -> Any:
        pass


class AnimatedSizeValue(AnimatedValue):
    def __init__(self, old_value: Size, new_value: Size) -> None:
        self.value: InterpolatedSize = InterpolatedSize(old_value, new_value)
        super().__init__(old_value, new_value)

    def _get_value(self, context: "AnimationContext") -> InterpolatedSize:
        self.value.progress = context.value
        return self.value


class AnimatedPositionValue(AnimatedValue):
    def __init__(self, old_value: Position, new_value: Position) -> None:
        self.value: InterpolatedPosition = InterpolatedPosition(old_value, new_value)
        super().__init__(old_value, new_value)

    def _get_value(self, context: "AnimationContext") -> InterpolatedPosition:
        self.value.progress = context.value
        return self.value


class AnimatedSpacingValue(AnimatedValue):
    def __init__(self, old_value: Spacing, new_value: Spacing) -> None:
        self.value: InterpolatedSpacing = InterpolatedSpacing(old_value, new_value)
        super().__init__(old_value, new_value)

    def _get_value(self, context: "AnimationContext") -> InterpolatedSpacing:
        self.value.progress = context.value
        return self.value
