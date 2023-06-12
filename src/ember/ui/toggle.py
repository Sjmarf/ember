import pygame
from typing import Optional, TYPE_CHECKING, Sequence, Union

from .. import common as _c
from ..event import TOGGLECLICKED
from .base.element import Element
from .base.interactive import Interactive
from ..utility.timer import BasicTimer

from ..size import SizeType, SequenceSizeType
from ..position import PositionType, CENTER, SequencePositionType
from ..state.state_controller import StateController

if TYPE_CHECKING:
    from ..style.toggle_style import ToggleStyle


class Toggle(Element, Interactive):
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
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Optional["ToggleStyle"] = None,
    ):
        self.set_style(style)

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

        Element.__init__(
            self,
            rect,
            pos,
            x,
            y,
            size,
            width,
            height,
            can_focus=True,
        )

        Interactive.__init__(self, disabled)

        self._timer = BasicTimer(
            self._w.value
            - round(self._h.value * self._style.handle_width_ratio)
            if self._is_active
            else 0
        )

    def __repr__(self) -> str:
        return "<Toggle>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)

        # Draw the base image

        self.state_controller.set_state(
            self._style.state_func(self),
            transitions=[
                self._style.base_material_transition,
                self._style.handle_material_transition,
            ],
        )

        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0],
                rect.y - surface.get_abs_offset()[1],
            ),
            rect.size,
            alpha,
            material_index=0
        )

        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0] + self._timer.val,
                rect.y - surface.get_abs_offset()[1],
            ),
            (round(self.rect.h * self._style.handle_width_ratio), rect.h),
            alpha,
            material_index=1
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

    def _set_style(self, style: Optional["ToggleStyle"]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional["ToggleStyle"]) -> None:
        """
        Sets the ToggleStyle of the Toggle.
        """
        self._style: "ToggleStyle" = self._get_style(style)

    def _set_active(self, state: bool) -> None:
        self.set_active(state)

    def set_active(self, state: bool, play_sound: bool = False) -> None:
        """
        Whether the Toggle is switched on or off.
        """
        self._is_active = state
        self._timer.play(
            stop=(
                self._w.value - round(self.rect.h * self._style.handle_width_ratio)
                if self._is_active
                else 0
            ),
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

    is_active: bool = property(
        fget=lambda self: self._is_active,
        fset=_set_active,
        doc="Whether the Toggle is on or off.",
    )

    style: "ToggleStyle" = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ToggleStyle of the Toggle. Synonymous with the set_style() method.",
    )
