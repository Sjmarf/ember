import json
from .. import common as _c
from typing import Union
try:
    from typing import Literal
except ModuleNotFoundError:
    from typing_extensions import Literal

import os

from .. import material
from .. import font
from .. import transition
from .. import style

import logging
import pygame

from ..size import FIT, FILL, Size

def load(style: Literal['stone', 'plastic', 'white', 'dark'] = 'dark',
         parts: Union[list[str], None] = None) -> dict:
    logging.debug(f"Loading style {style}")
    path = _c.package.joinpath(f'default_styles/{style}/data.json')
    return from_json(str(path), parts=parts, _ignore_ver=True)


def decode_element(data, styles):
    obj = None
    if data[0] == "Color":
        obj = material.Color
    elif data[0] == "AverageColor":
        obj = material.AverageColor
    elif data[0] == "Style":
        return styles[data[1]]
    elif data[0] == "Fade":
        obj = transition.Fade
    elif data[0] == "SurfaceFade":
        obj = transition.SurfaceFade
    elif data[0] == "Slide":
        obj = transition.Slide
    elif data[0] == "PixelFont":
        return font.PixelFont(filename=_c.package.joinpath(f'fonts/{data[1]}'))
    elif data[0] == "Font":
        return font.Font(pygame.font.SysFont(data[1], data[2]))
    elif data[0] == "RoundedRect":
        if isinstance(data[1][0], str):
            return material.shape.RoundedRect(material=decode_element(data[1], styles),
                                                    radius=data[2] if len(data) >= 3 else 20)
        else:
            return material.shape.RoundedRect(color=data[1],
                                                    radius=data[2] if len(data) >= 3 else 20)

    if obj:
        if type(data[1]) is dict:
            return obj(**data[1])
        else:
            return obj(data[1])


def from_json(filepath: Union[str, dict], set_as_default=True, parts: Union[list[str], None] = None,
              _ignore_ver: bool = False) -> dict:
    if type(filepath) is str:
        with open(filepath) as f:
            data = json.load(f)

        if data["pxui_version"] != _c.VERSION and not _ignore_ver:
            raise Exception(f"Can't load styles from json - PXUI version ({_c.VERSION}) does not match "
                            f"json file's version {data['pxui_version']}")

    else:
        data = json.load(filepath)

    asset_path = data.get("asset_directory")
    if asset_path is not None:
        asset_path = os.path.join(*os.path.split(filepath)[:-1], asset_path)
        asset_folders = os.listdir(asset_path)

    styles = {}

    for name, value in data["elements"].items():
        if parts is not None and name not in parts:
            continue
        assets = None
        if asset_path:
            if name in asset_folders:
                assets = os.listdir(f"{asset_path}/{name}")

        if (x := value.get('type')):
            element = x
            value.pop('type')
        else:
            element = name

        kwargs = dict()
        valid_file_names = dict()

        if element == "view":
            element_style = style.ViewStyle

        elif element == "stack":
            element_style = style.StackStyle

        elif element == "button":
            if assets:
                valid_file_names = {'default.png': 'material',
                                    'click.png': 'click_material',
                                    'hover.png': 'hover_material',
                                    'highlight.png': 'focus_material',
                                    'highlight_click.png': 'focus_click_material',
                                    'disabled.png': 'disabled_material',
                                    'click_down.ogg': 'click_down_sound',
                                    'click_up.ogg': 'click_up_sound'}

            element_style = style.ButtonStyle

        elif element == "text_field":
            if assets:
                valid_file_names = {'default.png': 'material',
                                    'active.png': 'active_material',
                                    'hover.png': 'hover_material',
                                    'disabled.png': 'disabled_material',
                                    'text_fade.png': 'text_fade'}

            element_style = style.TextFieldStyle

        elif element == "toggle":
            if assets:
                valid_file_names = {'base.png': 'base_image',
                                    'default.png': 'default_image',
                                    'hover.png': 'hover_image',
                                    'highlight.png': 'highlight_image',
                                    'switch_on.ogg': 'switch_on_sound',
                                    'switch_off.ogg': 'switch_off_sound'}

            element_style = style.ToggleStyle

        elif element == "slider":
            if assets:
                valid_file_names = {'base.png': 'base_image',
                                    'default.png': 'default_image',
                                    'hover.png': 'hover_image',
                                    'click.png': 'click_image',
                                    'focus.png': 'focus_image',
                                    'focus_click.png': 'focus_click_image'}

            element_style = style.SliderStyle

        elif element == "list":
            element_style = style.ListStyle

        elif element == "text":
            element_style = style.TextStyle

        elif element == "scroll":
            element_style = style.ScrollStyle

        else:
            raise ValueError(f"No element matching the name '{element}'.")

        if assets:
            for file in assets:
                if (k := valid_file_names.get(file)):
                    path = os.path.join(asset_path, name, file)
                    if file.endswith(".png") and file != "text_fade.png":
                        kwargs[k] = material.StretchedSurface(path, edge=data.get("image_edge"))
                    else:
                        kwargs[k] = path

        for k, v in value.items():
            if "size" in k and isinstance(v, list):
                for n, i in enumerate(v):
                    if isinstance(i, str):
                        if i == "FIT":
                            v[n] = FIT
                        elif i == "FILL":
                            v[n] = FILL
                    if isinstance(i, list):
                        size = Size(i[2], i[1], 0)
                        if i[0] == "FIT":
                            size.mode = 1
                        elif i[0] == "FILL":
                            size.mode = 2
                        v[n] = size

            elif isinstance(v, list):
                if output := decode_element(v, styles):
                    v = output

            kwargs[k] = v

        element_style = element_style(**kwargs)
        if set_as_default and element == name:
            element_style.set_as_default()

        styles[name] = element_style

    if "constants" in data.keys():
        styles.update(data["constants"])
    return styles