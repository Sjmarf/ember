import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING, Generator, Type

from ..common import SequenceElementType, DEFAULT
from ..event import CLICKEDDOWN, CLICKEDUP

from ..ui.h_stack import HStack
from ..ui.text import Text
from ember.base.can_disable import CanDisable
from ember.base.can_click import CanClick
from ember.base.can_focus import CanFocus
from ..base.element import Element
from ember.base.multi_element_container import MultiElementContainer
from ember.base.has_primary_child import HasPrimaryChild

from ..size import SizeType, OptionalSequenceSizeType, FIT
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)

if TYPE_CHECKING:
    pass

class Button(CanDisable, HasPrimaryChild, CanFocus, CanClick, MultiElementContainer):
    """
    A Button is an interactive Element. Buttons can hold exactly one child Element, which is rendered on the button.
    When the button is clicked, it will post the :code:`ember.BUTTONCLICKED` event.
    """

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        **kwargs,
    ):
        super().__init__(
            # MultiElementContainer
            *elements,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            # CanDisable
            disabled=disabled,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<Button>"

Button.w.default_value = FIT
Button.h.default_value = FIT