import json
from .. import common as _c
from typing import Union, Literal, IO, Optional, Type, Sequence
import os

from .. import ui
from .. import material
from .. import font
from .. import transition
from .. import style
from .. import state

import logging
import pygame

from ..size import FIT, FILL, Size, SizeMode


def _decode_element(data, styles):
    obj = None
    if isinstance(data[0], str) and "State" in data[0]:
        obj = getattr(state, data[0])
    elif data[0] == "Color":
        obj = material.Color
    elif data[0] == "AverageColor":
        obj = material.AverageColor
    elif data[0] == "Style":
        return styles[data[1]]
    elif data[0] == "Fade":
        obj = transition.Fade
    elif data[0] == "SurfaceFade":
        obj = transition.SurfaceFade
    elif data[0] == "PixelFont":
        return font.PixelFont(path=_c.package.joinpath(f"default_fonts/{data[1]}"))
    elif data[0] == "Font":
        return font.Font(pygame.font.SysFont(data[1], data[2]))
    elif data[0] == "IconFont":
        return font.IconFont(path=_c.package.joinpath(f"default_icon_fonts/{data[1]}"))
    elif data[0] in {"RoundedRect", "Capsule", "Ellipse"}:
        if data[0] == "RoundedRect":
            obj = material.shape.RoundedRect
        elif data[0] == "Capsule":
            obj = material.shape.Capsule
        elif data[0] == "Ellipse":
            obj = material.shape.Ellipse

        if isinstance(data[1][0], str):
            return obj(None, _decode_element(data[1], styles), *data[2:])
        else:
            return obj(None, data[1], *data[2:])

    if obj:
        if isinstance(data[1], dict):
            return obj(**data[1])
        else:
            return obj(data[1])


def _decode_size(
    size: Union[str, list]
) -> Union[Size, Sequence[Size], Sequence[int]]:
    if isinstance(size, str):
        if size == "FIT":
            return FIT
        elif size == "FILL":
            return FILL
    if isinstance(size, list):
        if len(size) == 3:
            new_size = Size(size[2], size[1], SizeMode.ABSOLUTE)
            if size[0] == "FIT":
                new_size.mode = SizeMode.FIT
            elif size[0] == "FILL":
                new_size.mode = SizeMode.FILL
            return new_size
        else:
            sizes = []
            for i in size:
                sizes.append(_decode_size(i))
            return sizes
    return size


def load(
    filepath: Union[str, IO],
    set_as_default=True,
    parts: Union[list[str], None] = None,
    _ignore_ver: bool = False,
) -> dict:
    """
    Loads default styles from a JSON file. Experimental.
    """
    if isinstance(filepath, str):
        if "." not in filepath:
            filepath = _c.package.joinpath(f"default_styles/{filepath}/data.json")

        with open(filepath) as f:
            data = json.load(f)

        if data["ember_version"] != _c.VERSION and not _ignore_ver:
            raise _c.Error(
                f"Can't load styles from json - Ember version ({_c.VERSION}) does not match "
                f"json file's version {data['ember_version']}"
            )

    else:
        data = json.load(filepath)

    asset_path = data.get("asset_directory")
    asset_folders = []
    if asset_path is not None:
        asset_path = os.path.join(*os.path.split(filepath)[:-1], asset_path)
        asset_folders = os.listdir(asset_path)

    styles = {}

    for name, value in data["elements"].items():
        if parts is not None and name not in parts:
            continue

        if x := value.get("type"):
            element = x
            value.pop("type")
        else:
            element = name

        kwargs = dict()
        valid_file_names = dict()

        element_folder: Optional[str] = None
        style_class: Optional[Type[style.Style]]
        default_for: list[Type[ui.Element]] = []

        if element == "View":
            element_folder = "view"
            valid_file_names = {
                "default.png": "default_material",
            }

            style_class = style.ViewStyle

        elif element == "Section":
            element_folder = "section"
            style_class = style.SectionStyle

        elif element in {"Container", "Stack", "VStack", "HStack", "Layout", "Box"}:
            element_folder = "container"
            style_class = style.ContainerStyle
            if element in {"Stack", "VStack", "HStack", "Layout", "Box"}:
                default_for = [getattr(ui, element)]

        elif element == "Button":
            element_folder = "button"
            valid_file_names = {
                "default.png": "default_material",
                "click.png": "click_material",
                "hover.png": "hover_material",
                "focus.png": "focus_material",
                "focus_click.png": "focus_click_material",
                "disabled.png": "disabled_material",
                "click_down.ogg": "click_down_sound",
                "click_up.ogg": "click_up_sound",
            }

            style_class = style.ButtonStyle

        elif element == "TextField":
            element_folder = "text_field"
            valid_file_names = {
                "default.png": "default_material",
                "active.png": "active_material",
                "hover.png": "hover_material",
                "disabled.png": "disabled_material",
                "text_fade.png": "text_fade",
            }

            style_class = style.TextFieldStyle

        elif element == "Toggle":
            element_folder = "toggle"
            valid_file_names = {
                "base.png": "default_base_material",
                "default.png": "default_handle_material",
                "hover.png": "hover_handle_material",
                "focus.png": "focus_handle_material",
                "disabled.png": "disabled_handle_material",
                "switch_on.ogg": "switch_on_sound",
                "switch_off.ogg": "switch_off_sound",
            }

            style_class = style.ToggleStyle

        elif element == "Slider":
            element_folder = "slider"
            valid_file_names = {
                "base.png": "default_base_material",
                "default.png": "default_handle_material",
                "hover.png": "hover_handle_material",
                "click.png": "click_handle_material",
                "focus.png": "focus_handle_material",
                "focus_click.png": "focus_click_handle_material",
                "disabled.png": "disabled_handle_material",
            }

            style_class = style.SliderStyle

        elif element == "Text":
            style_class = style.TextStyle

        elif element == "Icon":
            style_class = style.IconStyle

        elif element == "Scroll":
            style_class = style.ScrollStyle

        else:
            raise ValueError(f"No element matching the name '{element}'.")

        if name in asset_folders:
            element_folder = name

        if asset_path:
            if element_folder in asset_folders:
                for file in os.listdir(f"{asset_path}/{element_folder}"):
                    if k := valid_file_names.get(file):
                        path = os.path.join(asset_path, element_folder, file)
                        if file.endswith(".png") and file != "text_fade.png":
                            kwargs[k] = material.StretchedSurface(
                                path, edge=data.get("image_edge")
                            )
                        else:
                            kwargs[k] = path

        for k, v in value.items():
            if k == "sizes":
                new_v = {}
                for size_key, size in v.items():
                    if size_key in {"Stack", "VStack", "HStack", "Layout", "Box"}:
                        new_v[getattr(ui, size_key)] = _decode_size(size)
                v = new_v

            elif "size" in k and isinstance(v, list):
                for n, i in enumerate(v):
                    v[n] = _decode_size(i)

            elif isinstance(v, list):
                if output := _decode_element(v, styles):
                    v = output

            kwargs[k] = v

        element_style = style_class(**kwargs)
        if set_as_default and element == name:
            element_style.set_as_default(*default_for)

        styles[name] = element_style

    if "constants" in data.keys():
        styles.update(data["constants"])
    return styles
