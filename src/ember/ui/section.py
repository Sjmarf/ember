import pygame
from typing import TYPE_CHECKING, Union, Optional, Sequence

if TYPE_CHECKING:
    from .base.element import Element
    from ..style.section_style import SectionStyle
    from ..style.container_style import ContainerStyle
    from ..material.material import Material
    from ..state.background_state import BackgroundState
    from ..position import PositionType, SequencePositionType
    from ..size import SizeType, SequenceSizeType, OptionalSequenceSizeType

from .. import common as _c
from .. import log
from .box import Box


class Section(Box):
    """
    A subclass of Box that can itself be focused when using keyboard / controller navigation.
    """

    def __init__(
            self,
            element: Optional["Element"] = None,
            material: Union["BackgroundState", "Material", None] = None,
            rect: Union[pygame.rect.RectType, Sequence, None] = None,
            pos: Optional["SequencePositionType"] = None,
            x: Optional["PositionType"] = None,
            y: Optional["PositionType"] = None,
            size: "OptionalSequenceSizeType" = None,
            w: Optional["SizeType"] = None,
            h: Optional["SizeType"] = None,
            style: Optional["SectionStyle"] = None,
    ):
        super().__init__(element, material, rect, pos, x, y, size, w, h, style)

    def __repr__(self) -> str:
        return "<Section>"

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if direction in {_c.FocusDirection.IN, _c.FocusDirection.IN_FIRST}:
            log.nav.info(self, "Returning self.")
            return self

        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if direction == _c.FocusDirection.OUT:
            log.nav.info(self, f"Returning self.")
            return self
        elif (
            direction
            in {
                _c.FocusDirection.UP,
                _c.FocusDirection.DOWN,
                _c.FocusDirection.LEFT,
                _c.FocusDirection.RIGHT,
                _c.FocusDirection.FORWARD,
            }
            or self._element is None
        ):
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(self, f"-> child {self._element}.")
            return self._element._focus_chain(direction)

    def _event(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (
            event.type == pygame.JOYBUTTONDOWN and event.button == 0
        ):
            if self.layer.element_focused is self and self._element is not None:
                log.nav.info(self, "Enter key pressed, starting focus chain.")
                with log.nav.indent:
                    if self._element._can_focus:
                        self.layer.shift_focus(_c.FocusDirection.IN, element=self._element)
                log.nav.info(
                    self,
                    f"Focus chain ended. Focused {self.layer.element_focused}.",
                )
                return True

        return super()._event(event)
