import pygame
from typing import Optional, TYPE_CHECKING, Sequence, Union

from .. import common as _c
from ..event import TOGGLECLICKED
from .base.element import Element
from .base.styled import StyleMixin
from .base.interactive import InteractiveMixin
from ..utility.timekeeper import BasicTimekeeper

from ..size import SizeType, OptionalSequenceSizeType
from ..position import PositionType, CENTER, SequencePositionType
from ..state.state_controller import StateController

if TYPE_CHECKING:
    from ..style.toggle_style import ToggleStyle


class Toggle(InteractiveMixin, StyleMixin, Element):
    """
    A Toggle is an interactive Element. It is a switch that can either be on or off.

    When the toggle is clicked, it will post the :code:`ember.TOGGLECLICKED` event.
    """

    def __init__(
        self,
        active: bool = False,
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        style: Optional["ToggleStyle"] = None,
    ):
        self._is_active: bool = active

        self.is_hovered: bool = False
        """
        Is :code:`True` when the mouse is hovered over the Toggle. Read-only.
        """

        self.state_controller: StateController = StateController(self, materials=2)
        """
        The :py:class:`ember.state.StateController` object responsible for managing the Toggle's states.
        """

        self._disabled: bool = False

        super().__init__(
            # Element
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            style=style,
            can_focus=True,
            # Interactive
            disabled=disabled,
        )
        self._timer = BasicTimekeeper(
            int(self._is_active)
        )

    def __repr__(self) -> str:
        return "<Toggle>"

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

        # Base image

        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0],
                rect.y - surface.get_abs_offset()[1],
            ),
            rect.size,
            alpha,
            material_index=0,
        )

        # Handle image

        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0] + self._timer.val * (self._int_rect.w
                - round(self._int_rect.h * self._style.handle_width_ratio)),
                rect.y - surface.get_abs_offset()[1],
            ),
            (round(self.rect.h * self._style.handle_width_ratio), rect.h),
            alpha,
            material_index=1,
        )

    def _update(self) -> None:
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)
        self._timer.tick()

    def _event(self, event: pygame.event.Event) -> bool:
        if not self._disabled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered:
                    self.set_active(not self._is_active, play_sound=True)
                    return True

            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (
                event.type == pygame.JOYBUTTONDOWN and event.button == 0
            ):
                if self.layer.element_focused is self:
                    self.set_active(not self._is_active, play_sound=True)
                    return True

        return False

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self.set_active(value)

    def set_active(self, value: bool, play_sound: bool = False) -> None:
        """
        Whether the Toggle is switched on or off.
        """
        self._is_active = value
        self._timer.play(
            stop=int(self._is_active),
            duration=0.1,
        )

        event = pygame.event.Event(
            TOGGLECLICKED, element=self, is_active=self._is_active
        )
        pygame.event.post(event)

        if _c.audio_enabled and not _c.audio_muted and play_sound:
            sound = (
                self._style.switch_on_sound
                if self._is_active
                else self._style.switch_off_sound
            )
            if sound is not None:
                sound.play()
