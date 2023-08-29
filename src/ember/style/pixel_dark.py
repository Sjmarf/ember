from functools import cached_property
from .. import ui
from .. import font
from .. import material
from ..common import package


class PixelDark:
    background_color = (40, 40, 50)

    @cached_property
    def Text(self):
        class PixelDarkText(ui.Text):
            pass

        PixelDarkText.font_.default_value = font.PixelFont(
            path=package.joinpath(f"default_fonts/pixel")
        )
        PixelDarkText.primary_material_.default_value = material.Color("white")

        return PixelDarkText

    @cached_property
    def Icon(self):
        class PixelDarkIcon(ui.Icon):
            pass

        PixelDarkIcon.font_.default_value = font.IconFont(
            path=package.joinpath(f"default_icon_fonts/pixel")
        )
        PixelDarkIcon.primary_material_.default_value = material.Color("white")

        return PixelDarkIcon

    @cached_property
    def Button(self):
        root = package / "stylesets/pixel_dark/button"

        class PixelDarkButton(ui.PanelButton):
            text_class = self.Text

        PixelDarkButton.w_.default_value = 100
        PixelDarkButton.h_.default_value = 23

        PixelDarkButton.add_materials(
            default_material=root / "default.png",
            hover_material=root / "hover.png",
            click_material=root / "click.png",
            focus_material=root / "focus.png",
            focus_click_material=root / "focus_click.png",
            disabled_material=root / "disabled.png",
        )
        return PixelDarkButton

    @cached_property
    def ToggleButton(self):
        root = package / "stylesets/pixel_dark/button"

        class PixelDarkToggleButton(self.Button, ui.PanelToggleButton):
            pass

        PixelDarkToggleButton.add_materials(
            active_material=root / "active.png",
            active_hover_material=root / "active_hover.png",
            active_click_material=root / "active_click.png",
        )
        return PixelDarkToggleButton

    @cached_property
    def Switch(self):
        root = package / "stylesets/pixel_dark/toggle"

        class PixelDarkSwitch(ui.Switch):
            pass

        PixelDarkSwitch.add_materials(
            default_material=root / "base.png",
            default_handle_material=root / "default.png",
            hover_handle_material=root / "hover.png",
            focus_handle_material=root / "focus.png",
            disabled_handle_material=root / "disabled.png",
        )

        return PixelDarkSwitch

    @cached_property
    def HSwitch(self):
        class PixelDarkHSwitch(self.Switch, ui.HSwitch):
            pass

        PixelDarkHSwitch.w_.default_value = 30
        PixelDarkHSwitch.h_.default_value = 15

        return PixelDarkHSwitch

    @cached_property
    def VSwitch(self):
        class PixelDarkVSwitch(self.Switch, ui.VSwitch):
            pass

        PixelDarkVSwitch.w_.default_value = 15
        PixelDarkVSwitch.h_.default_value = 30

        return PixelDarkVSwitch
