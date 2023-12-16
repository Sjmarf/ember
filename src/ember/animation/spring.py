import math
from typing import Any, TYPE_CHECKING, Generator
from .animation import Animation, AnimationContext

if TYPE_CHECKING:
    from ember.trait.trait import Trait

from .. import common as _c



class Spring(Animation):
    def __init__(
        self, stiffness: float, mass: float, damping: float, weak: bool = False
    ) -> None:
        self.stiffness: float = stiffness
        self.mass: float = mass
        self.damping: float = damping
        super().__init__(weak=weak)


    def steps(self) -> Generator[float, None, None]:
        s: float = 1.0
        v: float = 0.0
        
        while True:
            spring_force = (-self.stiffness) * s
            damping_force = (-self.damping) * v

            a = (spring_force + damping_force) / self.mass
            
            new_v = a * _c.delta_time

            if v < 0 and new_v > 0 or v > 0 and new_v < 0:
                if abs(s) < 0.0001:
                    return
                
            v += a * _c.delta_time
            s += v * _c.delta_time
            yield 1-s
            