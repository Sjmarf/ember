from typing import TYPE_CHECKING, Union, Optional, Generator

from ember.base.element import Element

from ember import common as _c
from ember.axis import Axis, HORIZONTAL, VERTICAL
from ember.position import Position, PositionType, CENTER
from ember.size import Size, SizeType, FIT

from ember.trait.trait import Trait
from ember.size import load_size
from ember.position import load_position
from ember.trait.fake_trait import FakeTrait
from ember.trait.replacement_trait import ReplacementTrait
from ember.trait.conditional_cascading_trait_value import ConditionalCascadingTraitValue
from ember.trait.cascading_trait_value import CascadingTraitValue
from ember.base.container import Container

if TYPE_CHECKING:
    pass


class CanPivot(Element):
    
    def _axis_changed(self) -> None:
        if isinstance(self, Container):
            for value in self.cascading:
                if isinstance(value, ConditionalCascadingTraitValue):
                    ref = value.ref
                    self.start_cascade(value)
                    if value.ref != ref:
                        self.start_cascade(CascadingTraitValue(ref, None, value.depth))
    
    _axis: Trait[Axis] = Trait(
        default_value=HORIZONTAL,
        on_update=(
            lambda self: self.update_min_size_next_tick(must_update_parent=True),
            _axis_changed
            ),
        default_cascade_depth=1,        
    )
    
    pos1 = ReplacementTrait(
        default_value=CENTER,
        on_call=lambda self: Element.x if self._axis == HORIZONTAL else Element.y,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
        load_value_with=load_position,
    )

    pos2 = ReplacementTrait(
        default_value=CENTER,
        on_call=lambda self: Element.y if self._axis == HORIZONTAL else Element.x,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
        load_value_with=load_position,
    )

    size1 = ReplacementTrait(
        default_value=FIT,
        on_call=lambda self: Element.w if self._axis == HORIZONTAL else Element.h,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
        load_value_with=load_size,
    )

    size2 = ReplacementTrait(
        default_value=FIT,
        on_call=lambda self: Element.h if self._axis == HORIZONTAL else Element.w,
        on_update=lambda self: self.update_min_size_next_tick(must_update_parent=True),
        load_value_with=load_size,
    )

    @FakeTrait(posing_as=Element.x)
    def x(self):
        if self.axis == HORIZONTAL:
            return CanPivot.pos1
        return CanPivot.pos2

    @FakeTrait(posing_as=Element.y)
    def y(self):
        if self.axis == HORIZONTAL:
            return CanPivot.pos2
        return CanPivot.pos1

    @FakeTrait(posing_as=Element.w)
    def w(self):
        if self.axis == HORIZONTAL:
            return CanPivot.size1
        return CanPivot.size2

    @FakeTrait(posing_as=Element.h)
    def h(self):
        if self.axis == HORIZONTAL:
            return CanPivot.size2
        return CanPivot.size1

    def get_abs_size1(self, max_width: float = 0) -> float:
        return self.size1.get(self._min_size.size1, max_width, self.rect.h)

    def get_abs_size2(self, max_height: float = 0) -> float:
        return self.size2.get(self._min_size.size2, max_height, self.rect.w)
