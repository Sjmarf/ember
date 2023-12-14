import math
from typing import Any, TYPE_CHECKING
from .animation import Animation, AnimationContext

if TYPE_CHECKING:
    from ember.trait.trait import Trait

from .. import common as _c

class SpringAnimationContext(AnimationContext):
    def __init__(
        self, anim: "Spring", trait: "Trait", old_value: Any, new_value: Any
    ) -> None:
        super().__init__(anim, trait, old_value, new_value)
        self.position: float = 1
        self.velocity: float = 0
        self.increasing: bool = True

class Spring(Animation):
    def __init__(
        self, stiffness: float, mass: float, damping: float, weak: bool = False
    ) -> None:
        self.stiffness: float = stiffness
        self.mass: float = mass
        self.damping: float = damping
        super().__init__(weak=weak)

    def _update(self, context: "SpringAnimationContext") -> bool:
        s = context.position
        v = context.velocity

        spring_force = (-self.stiffness) * s
        damping_force = (-self.damping) * v

        a = (spring_force + damping_force) / self.mass
        v += a * _c.delta_time
        s += v * _c.delta_time

        context.velocity = v
        context.position = s

        context.value = 1 - context.position
        return False

    def create_context(
        self, trait: "Trait", old_value: Any, new_value: Any
    ) -> SpringAnimationContext:
        return SpringAnimationContext(self, trait, old_value, new_value)
