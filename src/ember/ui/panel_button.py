import pygame
from typing import Union, Optional, Sequence, Type

from .Button import Button

from ..material import Material
from ..material.blank import Blank

from .panel import Panel

from ..common import SequenceElementType, MaterialType

from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
    CENTER,
)

from ..event import BUTTONDOWN, BUTTONUP

from .text import Text
from ..on_event import on_event

from ..utility.load_material import load_material


class PanelButton(Button):
    default_material: Material = Blank()
    hover_material: Material = Blank()
    click_material: Material = Blank()
    focus_material: Material = Blank()
    focus_click_material: Material = Blank()
    disabled_material: Material = Blank()

    default_content_y = CENTER

    @classmethod
    def add_materials(
        cls,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        click_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        focus_click_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
    ) -> None:
        cls.default_material = load_material(default_material, None)
        cls.hover_material = load_material(hover_material, cls.default_material)
        cls.click_material = load_material(click_material, cls.hover_material)
        cls.focus_material = load_material(focus_material, cls.hover_material)
        cls.focus_click_material = load_material(
            focus_click_material, cls.click_material
        )
        cls.disabled_material = load_material(disabled_material, cls.default_material)

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
        **kwargs
    ):
        self.panel: Panel = Panel(self.default_material, y=0, size=FILL)

        super().__init__(
            self.panel,
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

    @on_event()
    def _update_panel_material(self) -> None:
        if self.disabled:
            self.panel.material = self.disabled_material
        elif self.clicked:
            self.panel.material = (
                self.focus_click_material if self.focused else self.click_material
            )
        elif self.focused:
            self.panel.material = self.focus_material
        elif self.hovered:
            self.panel.material = self.hover_material
        else:
            self.panel.material = self.default_material

    @on_event(BUTTONDOWN)
    def _update_content_y_down(self) -> None:
        self.content_y += 1

    @on_event(BUTTONUP)
    def _update_content_y_up(self) -> None:
        self.content_y -= 1
