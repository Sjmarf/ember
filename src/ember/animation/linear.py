from typing import Optional
from .animation import Animation, AnimationContext, SimpleAnimationContext

from .. import common as _c


class Linear(Animation):
    def __init__(self, duration: float):
        self.duration: float = duration

    def _update(self, context: "AnimationContext") -> bool:
        context.value += _c.delta_time / self.duration
        return context.value >= 1
