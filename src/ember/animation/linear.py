from typing import Optional
from .animation import Animation, AnimationContext

from .. import common as _c


class Linear(Animation):
    def __init__(self, duration: float, weak: bool = False) -> None:
        self.duration: float = duration
        super().__init__(weak=weak)

    def _update(self, context: "AnimationContext") -> bool:
        context.value += _c.delta_time / self.duration
        return context.value >= 1
