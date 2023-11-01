import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING

from ..common import SequenceElementType, ElementType

from ember.ui.can_disable import CanDisable
from ember.ui.can_click import CanClick
from ember.ui.can_focus import CanFocus
from ember.ui.single_element_container import SingleElementContainer

from ..size import SizeType, OptionalSequenceSizeType, FIT
from ember.position import (
    PositionType,
    SequencePositionType,
)

if TYPE_CHECKING:
    pass


class Button(CanDisable, CanFocus, CanClick, SingleElementContainer):
    """
    A Button is an interactive Element. Buttons can hold exactly one child Element, which is rendered on the button.
    When the button is clicked, it will post the :code:`ember.BUTTONCLICKED` event.
    """

    def __init__(
        self,
        element: Optional[ElementType] = None,
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
            element,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            disabled=disabled,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<Button>"


Button.w.default_value = FIT
Button.h.default_value = FIT
