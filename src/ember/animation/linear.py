from typing import Optional, Generator
from .animation import Animation, AnimationContext

from .. import common as _c


class Linear(Animation):
    def __init__(self, duration: float, weak: bool = False) -> None:
        self.duration: float = duration
        super().__init__(weak=weak)

    def steps(self) -> Generator[float, None, None]:
        progress = 0
        while progress < 1:
            progress += _c.delta_time / self.duration
            yield progress
