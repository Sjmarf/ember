from typing import Optional
from .size import Size, SizeType, load_size

from ember.axis import Axis, VERTICAL

from ember.trait.dependency_child import DependencyChild

class Interpolated(Size):
    """
    Used by animations to interpolate between two other Size objects.
    """
    
    old_size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)
    new_size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)

    def __init__(self, old_size: "Size", new_size: "Size", progress: float = 0) -> None:
        self._progress: float = progress
        self._old_size = None
        self._new_size = None
        super().__init__()
         
        self.old_size: "Size" = old_size
        self.new_size: "Size" = new_size

    def __eq__(self, other):
        if isinstance(other, Interpolated):
            return (
                self._progress == other._progress
                and self._old_size == other._old_size
                and self._new_size == other._new_size
            )
        return False
    
    def __hash__(self) -> int:
        return hash((self._progress, self._old_size, self._new_size))

    def __repr__(self) -> str:
        return f"<InterpolatedSize({self.old_size} -> {self.new_size}: {self.progress*100: .0f}%)>"

    def update_pair_value(self, value: float) -> bool:
        return self.new_size.update_pair_value(
            value
        ) or self.old_size.update_pair_value(value)

    def _get(self, *args, **kwargs) -> float:
        old_val = self.old_size.get(*args, **kwargs)
        new_val = self.new_size.get(*args, **kwargs)
        return round(old_val + (new_val - old_val) * self.progress)

    def copy(self) -> "Interpolated":
        return Interpolated(self.old_size, self.new_size, progress=self.progress)

    @property
    def progress(self) -> float:
        return self._progress
    
    @progress.setter
    @Size.triggers_trait_update
    def progress(self, value: float) -> None:
        self._progress = value    