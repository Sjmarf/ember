import pygame
from typing import Union, Optional, TYPE_CHECKING, Sequence

from .. import common as _c
from .base.element import Element
from .base.interactive import Interactive
from ..utility.timekeeper import BasicTimekeeper
from ..position import PositionType, SequencePositionType
from ..size import SizeType, OptionalSequenceSizeType
from ..event import SLIDERMOVED

from ..state.state_controller import StateController

if TYPE_CHECKING:
    from ..style.slider_style import SliderStyle


class Slider(Element, Interactive):
    """
    A Slider is an interactive Element. Given a lower and upper bound, it lets the user scroll between those two values.
    """

    def __init__(
        self,
        value: Optional[float] = None,
        min_value: float = 0,
        max_value: float = 100,
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        style: Union["SliderStyle", None] = None,
    ):

        Element.__init__(
            self,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            style,
            can_focus=True,
        )

        Interactive.__init__(self, disabled)

        self.min_value: float = min_value
        """
        The minimum value.
        """

        self.max_value: float = max_value
        """
        The maximum value.
        """

        self.is_hovered = False
        """
        Is :code:`True` when the mouse is hovered over the Slider. Read-only.
        """

        self.is_clicked = False
        """
        Is :code:`True` when the Slider is clicked down. Read-only.
        """

        self.is_clicked_keyboard = False
        """
        Is :code:`True` when the Slider is clicked down using keyboard / controller navigation. Read-only.
        """

        self.state_controller: StateController = StateController(self, materials=2)
        """
        The :py:class:`ember.state.StateController` object responsible for managing the Slider's states.
        """

        self._timer: BasicTimekeeper = BasicTimekeeper(value if value is not None else min_value)

    def __repr__(self):
        return "<Slider>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)

        self.state_controller.set_state(
            self._style.state_func(self),
            transitions=[
                self._style.base_material_transition,
                self._style.handle_material_transition,
            ],
        )

        # Draw the base image
        self.state_controller.render(
            surface, rect.topleft, rect.size, alpha, material_index=0
        )

        # Draw the handle image

        handle_width = round(self.rect.h * self._style.handle_width_ratio)

        self.state_controller.render(
            surface,
            (
                rect.x
                + (self._timer.val - self.min_value)
                / (self.max_value - self.min_value)
                * (self.rect.w - handle_width),
                rect.y,
            ),
            (handle_width, rect.h),
            alpha,
            material_index=1,
        )

    def _update(self) -> None:
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        if self.is_clicked:
            val = self._get_val_from_mouse_x(_c.mouse_pos[0])
            if (not self._timer.playing and self._timer.val != val) or (
                self._timer.playing and self._timer.stop_at != val
            ):
                self._timer.val = val
                self._timer.playing = False

        if self._timer.tick():
            self._post_event()

        if self.is_clicked_keyboard:
            if not self._timer.playing:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    self._move_handle(1)

                elif keys[pygame.K_LEFT]:
                    self._move_handle(-1)

                for joy in _c.joysticks:
                    axis = joy.get_axis(0)
                    if axis > 0.5:
                        self._move_handle(2)
                    elif axis < -0.5:
                        self._move_handle(-2)

    def _event(self, event: pygame.event.Event) -> bool:
        if not self._disabled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered:
                    self.is_clicked = True
                    self._timer.play(
                        self._get_val_from_mouse_x(_c.mouse_pos[0]), duration=0.2
                    )
                    return True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_clicked = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.layer.element_focused is self:
                        self.is_clicked_keyboard = not self.is_clicked_keyboard
                        return True

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if self.layer.element_focused is self:
                        self.is_clicked_keyboard = not self.is_clicked_keyboard
                        return True

                if self.is_clicked_keyboard:
                    if event.button == 1:
                        self.is_clicked_keyboard = False
                        return True

                    if event.button == 13:
                        self._move_handle(-1)
                        return True

                    if event.button == 14:
                        self._move_handle(1)
                        return True

            elif event.type == pygame.JOYHATMOTION:
                if self.is_clicked_keyboard:
                    if event.value == (1, 0):
                        self._move_handle(1)
                        return True

                    elif event.value == (-1, 0):
                        self._move_handle(-1)
                        return True

        return False

    def _on_unfocus(self) -> None:
        self.is_clicked_keyboard = False

    def _move_handle(self, direction: int = 1) -> None:
        self._timer.val = pygame.math.clamp(
            self._timer.val
            + _c.delta_time * (self.max_value - self.min_value) * direction,
            self.min_value,
            self.max_value,
        )

    def _post_event(self) -> None:
        event = pygame.event.Event(SLIDERMOVED, element=self, value=self._timer.val)
        pygame.event.post(event)

    def _set_disabled(self, value: bool) -> None:
        self.is_clicked = False
        self.is_clicked_keyboard = False

    def _get_val_from_mouse_x(self, mouse_x) -> float:
        handle_width = round(self.rect.h * self._style.handle_width_ratio)
        x = mouse_x - self.rect.x - handle_width / 2
        w = self.rect.w - handle_width
        return max(
            min(
                x / w * (self.max_value - self.min_value) + self.min_value,
                self.max_value,
            ),
            self.min_value,
        )

    @property
    def value(self) -> float:
        """
        Get or set the Slider's value. Limits are controlled by the :code:`min_value` and :code:`max_value` attributes.
        """
        return self._timer.val

    @value.setter
    def value(self, value: float) -> None:
        self.set_value(value)

    def set_value(self, value: float) -> None:
        self._timer.val = value
        self._post_event()