from abc import ABC, abstractmethod
from contextlib import nullcontext

from .interactive_gauge import InteractiveGauge
from .bar import Bar


from ember.animation import Animation, EaseInOut, EaseOut


class Slider(InteractiveGauge, Bar, ABC):
    click_animation: Animation | None = EaseInOut(0.1)

    def _set_progress(
        self, value: float, cause: InteractiveGauge.ValueCause.Cause
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
