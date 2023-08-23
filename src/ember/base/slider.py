import pygame
from abc import ABC, abstractmethod
from typing import Union, Optional, Sequence, TYPE_CHECKING
from enum import Enum

from ember import common as _c
from ember.common import SequenceElementType, DEFAULT
from ember.event import (
    BUTTONDOWN,
    BUTTONUP,
    SLIDERMOVED,
    SLIDERCONTROLACTIVATED,
    SLIDERCONTROLDEACTIVATED,
)

from ember.ui.base.mixin.interactive import Interactive
from ember.base.multi_element_container import MultiElementContainer
from ember.ui.base.mixin.content_pos_direction import DirectionalContentPos
from ember.ui.base.mixin.content_size_direction import DirectionalContentSize


from ember.size import SizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)

if TYPE_CHECKING:
    pass


class DragGesture:
    def __init__(self, start_location: tuple[float, float]) -> None:
        self.start_location: tuple[float, float] = start_location
        self.location: tuple[float, float] = start_location

    @property
    def translation(self) -> tuple[float, float]:
        return (
            self.location[0] - self.start_location[0],
            self.location[1] - self.start_location[1],
        )


class Slider(
    Interactive,
    DirectionalContentPos,
    DirectionalContentSize,
    MultiElementContainer,
    ABC,
):
    class MovementCause(Enum):
        DRAG = 0
        CLICK = 1
        SCROLL = 2
        KEY = 3
        SET = 4

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        min_value: float = 0,
        value: Optional[float] = 0,
        max_value: float = 100,
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
        style: Optional[StyleType] = DEFAULT,
    ):
        self.clicked: bool = False
        self.clicked_keyboard: bool = False
        self.gesture: Optional[DragGesture] = None

        self._min_value: float = min_value
        self._max_value: float = max_value

        self.handle_element_index: int = -1
        self.progress: float = 0
        if value is not None:
            self.value = value

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
            style=style,
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
        )

    def __repr__(self) -> str:
        return f"<Slider>"

    def _event(self, event: pygame.event.Event) -> bool:
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and not self._disabled
        ):
            self.clicked = self.hovered
            if self.clicked:
                self._click_down()
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked:
                self.clicked = False
                if not self._disabled:
                    if self.clicked_keyboard:
                        self.clicked_keyboard = False
                        self._post_slider_event(SLIDERCONTROLDEACTIVATED)
                    self._click_up()
                    return True

        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_RETURN
            and self.layer.element_focused is self
            and not self._disabled
        ):
            self.clicked_keyboard = not self.clicked_keyboard
            if self.clicked_keyboard:
                self._post_slider_event(SLIDERCONTROLACTIVATED)
            else:
                self._post_slider_event(SLIDERCONTROLDEACTIVATED)
            return True

        elif (
            event.type == pygame.JOYBUTTONDOWN
            and event.button == 0
            and self.layer.element_focused is self
            and not self._disabled
        ):
            self.clicked = True
            self._click_down()
            return True

        elif event.type == pygame.JOYBUTTONUP and event.button == 0:
            if self.clicked:
                self.clicked = False
                if self.layer.element_focused is self and not self._disabled:
                    self._click_up()
                    return True

        elif event.type == pygame.MOUSEMOTION and self.clicked:
            self.gesture.location = (
                _c.mouse_pos[0] - self.rect.x,
                _c.mouse_pos[1] - self.rect.y,
            )
            self.move_to_mouse()
            event = pygame.event.Event(SLIDERMOVED, element=self, gesture=self.gesture, cause=self.MovementCause.DRAG)
            self._post_event(event)

        return False

    def _click_down(self):
        self.gesture = DragGesture(
            (_c.mouse_pos[0] - self.rect.x, _c.mouse_pos[1] - self.rect.y)
        )
        self.move_to_mouse()
        event = pygame.event.Event(SLIDERMOVED, element=self, gesture=None, cause=self.MovementCause.CLICK)
        self._post_event(event)
        self._post_slider_event(BUTTONDOWN)

    def _click_up(self):
        self.gesture = None
        self._post_slider_event(BUTTONUP)

    def _post_slider_event(self, event_type: int) -> None:
        event = pygame.event.Event(event_type, element=self)
        self._post_event(event)

    def _on_unfocus(self) -> None:
        if self.clicked_keyboard:
            self.clicked_keyboard = False
            self._post_slider_event(BUTTONUP)

    @property
    def value(self) -> float:
        return self._min_value + self.progress * (self._max_value - self._min_value)

    @value.setter
    def value(self, value: float) -> None:
        if self.progress != (
            progress := pygame.math.clamp(
                (value - self._min_value) / (self._max_value - self._min_value), 0, 1
            )
        ):
            self.progress = progress
            event = pygame.event.Event(SLIDERMOVED, element=self, gesture=None, cause=self.MovementCause.SET)
            self._post_event(event)

    @property
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, value: min_value) -> None:
        if self._min_value != value:
            current_value = self.value
            self._min_value = value
            self.value = current_value

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: min_value) -> None:
        if self._max_value != value:
            current_value = self.value
            self._max_value = value
            self.value = current_value

    @abstractmethod
    def move_to_mouse(self) -> None:
        ...

    def shift_value(self, value: float, cause=MovementCause.SET) -> None:
        self.progress = pygame.math.clamp(self.progress + value, 0, 1)
        event = pygame.event.Event(SLIDERMOVED, element=self, gesture=None, cause=cause)
        self._post_event(event)
