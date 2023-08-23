import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING, Generator, Type

from ..common import SequenceElementType, DEFAULT
from ..event import BUTTONDOWN, BUTTONUP

from ..ui.h_stack import HStack
from ..ui.text import Text
from ember.base.interactive import Interactive
from ..base.element import Element
from ember.base.multi_element_container import MultiElementContainer
from ..base.content_pos import ContentPos
from ember.base.content_size import ContentSize

from ..size import SizeType, OptionalSequenceSizeType, FIT
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)

if TYPE_CHECKING:
    pass


class Button(Interactive, ContentPos, ContentSize, MultiElementContainer):
    """
    A Button is an interactive Element. Buttons can hold exactly one child Element, which is rendered on the button.
    When the button is clicked, it will post the :code:`ember.BUTTONCLICKED` event.
    """

    default_w = FIT
    default_h = FIT

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
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        **kwargs,
    ):
        self.primary_element_index: int = -1
        """
        The index of the element that is considered the 'main' child element of the button.
        """

        self.clicked: bool = False
        """
        Is :code:`True` when the button is clicked down. Read-only.
        """

        super().__init__(
            # MultiElementContainer
            elements,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            # ContentPos
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            # ContentSize
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
            # Interactive
            disabled=disabled,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<Button>"

    def _event(self, event: pygame.event.Event) -> bool:
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and not self._disabled
        ):
            self.clicked = self.hovered
            if self.clicked:
                self._post_button_event(BUTTONDOWN)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked:
                self.clicked = False
                if not self._disabled:
                    self._post_button_event(BUTTONUP)
                    return True

        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_RETURN
            and self.layer.element_focused is self
            and not self._disabled
        ):
            self.clicked = True
            self._post_button_event(BUTTONDOWN)
            return True

        elif event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            if self.clicked:
                self.clicked = False
                if self.layer.element_focused is self and not self._disabled:
                    self._post_button_event(BUTTONUP)
                    return True

        elif (
            event.type == pygame.JOYBUTTONDOWN
            and event.button == 0
            and self.layer.element_focused is self
            and not self._disabled
        ):
            self.clicked = True
            self._post_button_event(BUTTONDOWN)
            return True

        elif event.type == pygame.JOYBUTTONUP and event.button == 0:
            if self.clicked:
                self.clicked = False
                if self.layer.element_focused is self and not self._disabled:
                    self._post_button_event(BUTTONUP)
                    return True

        return False

    def _post_button_event(self, event_type: int) -> None:
        text = (
            self._elements[self.primary_element_index].text
            if isinstance(self._elements[self.primary_element_index], Text)
            else None
        )
        event = pygame.event.Event(event_type, element=self, text=text)
        self._post_event(event)

    @property
    def element(self) -> Optional["Element"]:
        return self._elements[self.primary_element_index]

    @element.setter
    def element(self, *element: Optional[SequenceElementType]) -> None:
        self.set_element(*element)

    def set_element(
        self,
        *element: Optional[SequenceElementType],
        _update: bool = True,
    ) -> None:
        """
        Replace the child element of the Button.
        """

        if element:
            if not isinstance(element[0], str) and isinstance(
                element[0], (Sequence, Generator)
            ):
                element = list(element[0])
                if not element:
                    element = (None,)

        else:
            element = (None,)

        if (
            element[0] is not self._elements[self.primary_element_index]
            or len(element) > 1
        ):
            if len(element) > 1:
                element = HStack(element)

            with self.adding_element(element):
                self._elements[self.primary_element_index] = element
