from abc import ABC, abstractmethod
from contextlib import nullcontext

from .interactive_linear_gauge import InteractiveLinearGauge
from .slider import Slider


from ember.animation import Animation, EaseInOut, EaseOut


class InteractiveSlider(InteractiveLinearGauge, Slider, ABC):
    click_animation: Animation | None = EaseInOut(0.1)

    def _move_to_mouse_pos(
        self, cause: InteractiveLinearGauge.ValueCause.Cause, padding: int = 0
    ) -> None:
        super()._move_to_mouse_pos(cause=cause, handle_rect=self._handle.rect)

    def _set_progress(
        self, value: float, cause: InteractiveLinearGauge.ValueCause.Cause, **kwargs
    ) -> None:
        animation = nullcontext()
        if (
            cause
            in {self.ValueCause.CLICK, self.ValueCause.KEY}
            and self.click_animation is not None
        ):
            animation = self.click_animation
        with animation:
            super()._set_progress(value, cause, animation=animation)
