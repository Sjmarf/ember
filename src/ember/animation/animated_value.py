from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from ..size import Size, InterpolatedSize
from ..position import Position, InterpolatedPosition

if TYPE_CHECKING:
    from .animation import AnimationContext
    from ..ui.base.element import Element

class AnimatedValue(ABC):  
    @abstractmethod
    def _get_value(self, context: "AnimationContext") -> Any:
        pass
    
    def _get_finish_value(self, context: "AnimationContext") -> Any:
        pass    


class AnimatedSizeValue(AnimatedValue):
    def __init__(self, old_value: Size, new_value: Size) -> None:
        self.new_value: Size = new_value
        self.value: InterpolatedSize = InterpolatedSize(old_value, new_value)

    def _get_value(self, context: "AnimationContext") -> InterpolatedSize:
        self.value.progress = context.progress / context.anim.duration  
        return self.value
    
    def _get_finish_value(self, context: "AnimationContext") -> Size:
        return self.new_value
    
class AnimatedPositionValue(AnimatedValue):
    def __init__(self, old_value: Size, new_value: Size) -> None:
        self.new_value: Position = new_value
        self.value: InterpolatedPosition = InterpolatedPosition(old_value, new_value)

    def _get_value(self, context: "AnimationContext") -> InterpolatedPosition:
        self.value.progress = context.progress / context.anim.duration  
        return self.value
    
    def _get_finish_value(self, context: "AnimationContext") -> Position:
        return self.new_value
