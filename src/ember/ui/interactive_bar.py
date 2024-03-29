from abc import ABC, abstractmethod
from contextlib import nullcontext

from .interactive_linear_gauge import InteractiveLinearGauge
from .bar import Bar


from ember.animation import Animation, EaseInOut, EaseOut


class InteractiveBar(InteractiveLinearGauge, Bar, ABC):
    click_animation: Animation | None = EaseInOut(0.1)

    def _set_progress(
        self, value: float, cause: InteractiveLinearGauge.ValueCause.Cause
    ) -> None:
        animation = nullcontext()
        if (
            cause
            in {self.ValueCause.CLICK, self.ValueCause.PROPERTY, self.ValueCause.KEY}
            and self.click_animation is not None
        ):
            animation = self.click_animation
        with animation:
            super()._set_progress(value, cause)
