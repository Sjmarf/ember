from functools import cached_property
from typing import Type
from .. import ui
from .. import font
from .. import material
from ..common import package

from ..size import AbsoluteSize


class PixelDark:
    @cached_property
    def Text(self):
        class Text(ui.Text):
            pass

        Text.font_.default_value = font.PixelFont(path=package.joinpath(f"default_fonts/pixel"))
        Text.primary_material_.default_value = material.Color("white")

        return Text

    @cached_property
    def Button(self):
        root = package / "stylesets/pixel_dark/button"

        class Button(ui.PanelButton):
            text_class = self.Text

        Button.w_.default_value = AbsoluteSize(100)
        Button.h_.default_value = AbsoluteSize(23)

        Button.add_materials(
            default_material=root / "default.png",
            hover_material=root / "hover.png",
            click_material=root / "click.png",
            focus_material=root / "focus.png",
            focus_click_material=root / "focus_click.png",
            disabled_material=root / "disabled.png",
        )
        return Button
