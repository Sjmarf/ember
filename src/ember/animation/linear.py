from typing import Any, TYPE_CHECKING
from .animation import Animation, AnimationContext, ESCAPING

from .. import common as _c

from ..size import InterpolatedSize

if TYPE_CHECKING:
    from ..ui.base.element import Element


class Linear(Animation):
    def __init__(self, duration: float) -> None:
        self.duration: float = duration
        super().__init__()

    def _update(self, context: AnimationContext) -> bool:
        values = {k: v._get_value(context) for k,v in context.values.items()}
        context.func(**values)
        
        context.progress += _c.delta_time
        if context.progress >= self.duration:
            return True
        return False

    def create_context(
        self, element: "Element", func: callable, values: dict[str, Any]
    ) -> AnimationContext:
        return AnimationContext(element, self, func, values)
    
    def _finish(self, context: AnimationContext) -> None:
        values = {k: v._get_finish_value(context) for k,v in context.values.items()}
        context.func(**values)
