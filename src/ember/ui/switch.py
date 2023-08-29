import abc
from typing import Optional, Union, Sequence
from abc import ABC
import pygame

from ..base.directional import Directional
from ..base.content_size_direction import (
    DirectionalContentSize,
    HorizontalContentSize,
    VerticalContentSize,
)
from ..base.content_pos_direction import (
    DirectionalContentPos,
    HorizontalContentPos,
    VerticalContentPos,
)

from .toggle_button import ToggleButton
from ..material import Material
from ..material.blank import Blank

from ..event import TOGGLEON, TOGGLEOFF

from ..size import SizeType, OptionalSequenceSizeType, FILL, RATIO
from ember.position import (
    Position,
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
)

from ..animation.animation import Animation
from ..animation.ease import EaseInOut

from .panel import Panel
from ..common import MaterialType, SequenceElementType
from ..utility.load_material import load_material

from ..on_event import on_event


class Switch(DirectionalContentPos, DirectionalContentSize, ToggleButton, ABC):
    default_material: Material = Blank()
    hover_material: Material = Blank()
    focus_material: Material = Blank()
    disabled_material: Material = Blank()
    default_handle_material: Material = Blank()
    hover_handle_material: Material = Blank()
    focus_handle_material: Material = Blank()
    disabled_handle_material: Material = Blank()
    animation: Animation = EaseInOut(0.2)

    active_position: Position = NotImplemented
    inactive_position: Position = NotImplemented

    @classmethod
    def add_materials(
        cls,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
        default_handle_material: Optional[MaterialType] = None,
        hover_handle_material: Optional[MaterialType] = None,
        focus_handle_material: Optional[MaterialType] = None,
        disabled_handle_material: Optional[MaterialType] = None,
    ) -> None:
        cls.default_material = load_material(
            default_material, cls.default_material, None
        )
        cls.hover_material = load_material(
            hover_material, cls.hover_material, cls.default_material
        )
        cls.focus_material = load_material(
            focus_material, cls.focus_material, cls.hover_material
        )
        cls.disabled_material = load_material(
            disabled_material, cls.disabled_material, cls.disabled_material
        )

        cls.default_handle_material = load_material(
            default_handle_material, cls.default_handle_material, None
        )
        cls.hover_handle_material = load_material(
            hover_handle_material,
            cls.hover_handle_material,
            cls.default_handle_material,
        )
        cls.focus_handle_material = load_material(
            focus_handle_material, cls.focus_handle_material, cls.hover_handle_material
        )
        cls.disabled_handle_material = load_material(
            disabled_handle_material,
            cls.disabled_handle_material,
            cls.disabled_handle_material,
        )

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
        self.panel: Panel = Panel(self.default_material, y=0, size=FILL)
        self.handle_panel: Panel = Panel(self.default_handle_material)

        super().__init__(
            self.panel,
            self.handle_panel,
            *elements,
            active=active,
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

        self.parallel_content_pos = self.active_position if active else self.inactive_position
        self.perpendicular_content_size = FILL
        self.parallel_content_size = RATIO

    @on_event()
    def _update_panel_material(self) -> None:
        if self.disabled:
            self.panel.material = self.disabled_material
            self.handle_panel.material = self.disabled_handle_material
        elif self.focused:
            self.panel.material = self.focus_material
            self.handle_panel.material = self.focus_handle_material
        elif self.hovered:
            self.panel.material = self.hover_material
            self.handle_panel.material = self.hover_handle_material
        else:
            self.panel.material = self.default_material
            self.handle_panel.material = self.default_handle_material

    @on_event(TOGGLEON)
    def _move_handle_active(self):
        with self.animation:
            self.parallel_content_pos = self.active_position

    @on_event(TOGGLEOFF)
    def _move_handle_inactive(self):
        with self.animation:
            self.parallel_content_pos = self.inactive_position


class HSwitch(Switch, HorizontalContentSize, HorizontalContentPos):
    active_position = RIGHT
    inactive_position = LEFT


class VSwitch(Switch, VerticalContentSize, VerticalContentPos):
    active_position = TOP
    inactive_position = BOTTOM
