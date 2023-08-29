import pygame
from ..common import SequenceElementType, DEFAULT
from typing import Optional, Union, Sequence
from ember.position import (
    PositionType,
    OptionalSequencePositionType,
    SequencePositionType,
)
from ..size import SizeType, OptionalSequenceSizeType
from .button import Button
from ..event import TOGGLEON, TOGGLEOFF

from ..event import BUTTONDOWN
from ..on_event import on_event

from .text import Text

class ToggleButton(Button):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        active: bool = False,
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        **kwargs
    ):
        super().__init__(
            *elements,
            disabled=disabled,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
            **kwargs
        )

        self._active: bool = active

    def _post_button_event(self, event_type: int) -> None:
        text = (
            self._elements[self.primary_element_index].text
            if isinstance(self._elements[self.primary_element_index], Text)
            else None
        )
        event = pygame.event.Event(event_type, element=self, text=text, active=self.active)
        self._post_event(event)

    @on_event(BUTTONDOWN)
    def _toggle_active(self):
        self._active = not self._active
        self._post_button_event(TOGGLEON if self._active else TOGGLEOFF)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        if self._active != value:
            self._active = value
            self._post_button_event(TOGGLEON if self._active else TOGGLEOFF)
