from typing import Optional
from .animation import SimpleAnimation, SimpleAnimationContext

from .. import common as _c


class EaseIn(SimpleAnimation):

    def _update(self, context: "SimpleAnimationContext") -> True:
        context.progress += _c.delta_time / self.duration
        context.value = context.progress**2
        return context.progress >= 1


class EaseOut(SimpleAnimation):

    def _update(self, context: "SimpleAnimationContext") -> bool:
        context.progress += _c.delta_time / self.duration
        context.value += _c.delta_time / self.duration
        context.value = context.progress * (2 - context.progress)
        return context.progress >= 1


class EaseInOut(SimpleAnimation):

    def _update(self, context: "SimpleAnimationContext") -> bool:
        context.progress += _c.delta_time / self.duration
        x = context.progress
        if x < 0.5:
            context.value = 2 * x**2
        else:
            x -= 0.5
            context.value = 2 * x * (1 - x) + 0.5
        return context.progress >= 1
