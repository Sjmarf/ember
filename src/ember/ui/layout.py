import math
import pygame
from ..common import INHERIT, InheritType
from typing import Union, Optional, Sequence

from .base.multi_element_container import MultiElementContainer
from .. import log
from ..size import FILL, SizeType, SequenceSizeType
from .view import ViewLayer
from .base.element import Element
from ..state.state_controller import StateController
from ..state.state import State, load_background
from ..position import PositionType

from ..style.container_style import ContainerStyle


class Layout(MultiElementContainer):
    def __init__(
        self,
        *elements: Union[Element, Sequence[Element]],
        background: Optional[State] = None,
        focus_self: Union[InheritType, bool] = INHERIT,
        position: PositionType = None,
        size: SequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
        style: Optional[ContainerStyle] = None,
    ):
        self.layer: Optional[ViewLayer] = None
        self.parent: Optional[Element] = None

        self.set_style(style)

        self.background: Optional[State] = load_background(self, background)
        """
        The background :py:class:`State<ember.state.State>` of the Layout. Overrides all ContainerStyle materials.
        """

        self.focus_self: bool = (
            self._style.focus_self if focus_self is INHERIT else focus_self
        )
        """
        Modifies how the Layout behaves with keyboard / controller navigation. If set to True, the Layout itself 
        is focusable. If you press enter when the Layout is focused, the first child of the Layout is focused.
        """

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object is responsible for managing the Layout's 
        background materials.
        """

        self._elements = []
        self.set_elements(*elements, _supress_update=True)
        super().__init__(
            position,
            size,
            width,
            height,
            default_size=(
                FILL,
                FILL,
            ),
        )

        self._fit_width: float = 0
        self._fit_height: float = 0

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
        self,
        surface: pygame.Surface,
        pos: tuple[float, float],
        max_size: tuple[float, float],
        _ignore_fill_width: bool = False,
        _ignore_fill_height: bool = False,
    ) -> None:
        self_width = self.get_abs_width(max_size[0])
        self_height = self.get_abs_height(max_size[1])

        for element in self.elements:
            x = pos[0] + element.position[0].get(
                element, self_width, element.get_abs_width(max_size[0])
            )
            y = pos[1] + element.position[1].get(
                element, self_height, element.get_abs_height(max_size[1])
            )
            element._update_rect_chain_down(surface, (x, y), max_size)

        super()._update_rect_chain_down(
            surface, pos, max_size, _ignore_fill_width, _ignore_fill_height
        )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._width.mode == 1:
            self._fit_width = 0
            for i in self._elements:
                if i._width.mode == 2:
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width Layout."
                    )
                if (w := i.get_abs_width()) > self._fit_width:
                    self._fit_width = w
            else:
                self._fit_width = 20

        if self._height.mode == 1:
            self._fit_height = 0
            for i in self._elements:
                if i._height.mode == 2:
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height Layout."
                    )
                if (h := i.get_abs_height()) > self._fit_height:
                    self._fit_height = h
            else:
                self._fit_height = 20

    def _focus_chain(self, previous=None, direction: str = "in") -> Element:
        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

        element = None
        if direction in {"in", "in_first"}:
            if self.focus_self:
                log.nav.info(self, "Returning self.")
                return self
            else:
                log.nav.info(self, f"-> child {self._elements[0]}.")
                element = self._elements[0]

        elif direction == "out":
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self
            else:
                log.nav.info(self, f"-> parent {self.parent}.")
                return self.parent._focus_chain(self, direction=direction)

        elif direction == "forward":
            if self.layer.element_focused is not self._elements[-1]:
                index = self._elements.index(self.layer.element_focused)
                element = self._elements[index + 1]

        elif direction == "backward":
            if self.layer.element_focused is not self._elements[0]:
                index = self._elements.index(self.layer.element_focused)
                element = self._elements[index - 1]

        else:
            closest_distance = math.inf
            element = None
            for i in self._elements:
                if direction == "right":
                    if i.rect.x <= self.layer.element_focused.rect.x:
                        continue
                elif direction == "left":
                    if i.rect.x >= self.layer.element_focused.rect.x:
                        continue
                elif direction == "up":
                    if i.rect.y >= self.layer.element_focused.rect.y:
                        continue
                elif direction == "down":
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
            return self.parent._focus_chain(previous=self, direction=direction)

        else:
            log.nav.info(self, f"-> child {element}.")
            return element._focus_chain(None)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.layer.element_focused is self:
                    log.nav.info(self, "Enter key pressed, starting focus chain.")
                    with log.nav.indent:
                        self.layer._focus_element(self._elements[0])
                    log.nav.info(
                        self,
                        f"Focus chain ended. Focused {self.layer.element_focused}.",
                    )
                    return True

        for i in self._elements:
            if i._event(event):
                return True
        return False
