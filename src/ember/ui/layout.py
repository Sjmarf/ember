import math
import pygame
from .. import common as _c
from ..common import INHERIT, InheritType, FocusType, FOCUS_CLOSEST, FOCUS_FIRST
from typing import Union, Optional, Sequence, TYPE_CHECKING, Literal

from .base.multi_element_container import MultiElementContainer
from .. import log
from ..size import FILL, SizeType, SequenceSizeType, SizeMode
from .view import ViewLayer
from .base.element import Element
from ..state.state_controller import StateController
from ..state.state import State, load_background
from ..position import PositionType, CENTER, SequencePositionType

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle
    from ..material import Material


class Layout(MultiElementContainer):
    def __init__(
        self,
        *elements: Union[Element, Sequence[Element]],
        material: Union["State", "Material", None] = None,
        focus_on_entry: Union[InheritType, FocusType] = INHERIT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        self.layer: Optional[ViewLayer] = None
        self.parent: Optional[Element] = None

        self.set_style(style)

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object is responsible for managing the Layout's 
        background materials.
        """

        self._elements = []
        self.set_elements(*elements, _update=False)
        super().__init__(material, rect, pos, x, y, size, width, height, focus_on_entry)

        self._min_w: float = 0
        self._min_h: float = 0

        self._update_elements()

    def __repr__(self) -> str:
        return f"<Layout({len(self._elements)} elements)>"

    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        for i in self._elements:
            i._render_a(surface, offset, alpha=alpha)

    def _update(self) -> None:
        for i in self._elements:
            i._update_a()

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:

        super()._update_rect_chain_down(
            surface, x, y, w, h
        )

        for element in self.elements:
            element_x_obj = element._x if element._x is not None else CENTER
            element_y_obj = element._y if element._y is not None else CENTER

            element_w = element.get_abs_width(w - abs(element_x_obj.value))
            element_h = element.get_abs_height(h - abs(element_y_obj.value))

            element_x = x + element_x_obj.get(
                element,
                w,
                element_w
            )
            element_y = y + element_y_obj.get(
                element,
                h,
                element_h
            )
            element._update_rect_chain_down(
                surface,
                element_x, element_y,
                element_w, element_h
            )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._w.mode == SizeMode.FIT:
            self._min_w = 0
            for i in self._elements:
                if i._w.mode == SizeMode.FILL:
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width Layout."
                    )
                if (w := i.get_abs_width()) > self._min_w:
                    self._min_w = w
            else:
                self._min_w = 20

        if self._h.mode == SizeMode.FIT:
            self._min_h = 0
            for i in self._elements:
                if i._h.mode == SizeMode.FILL:
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height Layout."
                    )
                if (h := i.get_abs_height()) > self._min_h:
                    self._min_h = h
            else:
                self._min_h = 20

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        element = None
        if (
            direction in {_c.FocusDirection.IN, _c.FocusDirection.IN_FIRST}
            and self.focus_on_entry is FOCUS_FIRST or direction == _c.FocusDirection.SELECT
        ):
            log.nav.info(self, f"-> child {self._elements[0]}.")
            element = self._elements[0]

        elif direction == _c.FocusDirection.OUT:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        elif direction == _c.FocusDirection.FORWARD:
            if self.layer.element_focused is not self._elements[-1]:
                index = self._elements.index(self.layer.element_focused)
                element = self._elements[index + 1]

        elif direction == _c.FocusDirection.BACKWARD:
            if self.layer.element_focused is not self._elements[0]:
                index = self._elements.index(self.layer.element_focused)
                element = self._elements[index - 1]

        else:
            closest_distance = math.inf
            for i in self._elements:
                if direction == _c.FocusDirection.RIGHT:
                    if i.rect.x <= self.layer.element_focused.rect.x:
                        continue
                elif direction == _c.FocusDirection.LEFT:
                    if i.rect.x >= self.layer.element_focused.rect.x:
                        continue
                elif direction == _c.FocusDirection.UP:
                    if i.rect.y >= self.layer.element_focused.rect.y:
                        continue
                elif direction == _c.FocusDirection.DOWN:
                    if i.rect.y <= self.layer.element_focused.rect.y:
                        continue

                dist = math.sqrt(
                    (i.rect.x - self.layer.element_focused.rect.x) ** 2
                    + (i.rect.y - self.layer.element_focused.rect.y) ** 2
                )

                if dist < closest_distance:
                    element = i
                    closest_distance = dist

        if element is None:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(self, f"-> child {element}.")
            return element._focus_chain(_c.FocusDirection.IN)

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements:
            if i._event(event):
                return True
        return False
