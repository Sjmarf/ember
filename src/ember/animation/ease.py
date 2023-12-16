from typing import Optional, Generator
from .animation import Animation

from .. import common as _c


class EaseIn(Animation):
    def __init__(self, duration: float, weak: bool = False) -> None:
        self.duration: float = duration
        super().__init__(weak=weak)

    def steps(self) -> Generator[float, None, None]:
        progress = 0
        while progress < 1:
            progress += _c.delta_time / self.duration
            yield progress**2


class EaseOut(Animation):
    def __init__(self, duration: float, weak: bool = False) -> None:
        self.duration: float = duration
        super().__init__(weak=weak)
    
    def steps(self) -> Generator[float, None, None]:
        progress = 0
        while progress < 1:
            progress += _c.delta_time / self.duration
            yield progress * (2 - progress)


class EaseInOut(Animation):
    def __init__(self, duration: float, weak: bool = False) -> None:
        self.duration: float = duration
        super().__init__(weak=weak)
    
    def steps(self) -> Generator[float, None, None]:
        progress = 0
        while progress < 0.5:
            progress += _c.delta_time / self.duration
            yield 2 * progress ** 2
        while progress < 1:
            progress += _c.delta_time / self.duration
            yield 2 * (progress - 0.5) * (1.5 - progress) + 0.5