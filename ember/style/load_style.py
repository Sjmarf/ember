import json
from ember import common as _c
from typing import Union, Literal
import os
import ember.style
import ember.material
import ember.font
import logging
import pygame


def load(style: Literal['stone', 'plastic', 'white', 'dark'], parts: Union[list[str], None] = None) -> dict:
    logging.debug(f"Loading style {style}")
    path = _c.package.joinpath(f'default_styles/{style}/data.json')
    return from_json(str(path), parts=parts, _ignore_ver=True)


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
            style = ember.style.ViewStyle

        elif element == "button":
            if assets:
                valid_file_names = {'default.png': 'default_image',
                                    'click.png': 'click_image',
                                    'hover.png': 'hover_image',
                                    'highlight.png': 'highlight_image',
                                    'highlight_click.png': 'highlight_clicked_image',
                                    'disabled.png': 'disabled_image',
                                    'click_down.ogg': 'click_down_sound',
                                    'click_up.ogg': 'click_up_sound'}

            style = ember.style.ButtonStyle

        elif element == "text_field":
            if assets:
                valid_file_names = {'default.png': 'default_image',
                                    'active.png': 'active_image',
                                    'hover.png': 'hover_image',
                                    'disabled.png': 'disabled_image',
                                    'text_fade.png': 'text_fade'}

            style = ember.style.TextFieldStyle

        elif element == "toggle":
            if assets:
                valid_file_names = {'base.png': 'base_image',
                                    'default.png': 'default_image',
                                    'hover.png': 'hover_image',
                                    'highlight.png': 'highlight_image',
                                    'switch_on.ogg': 'switch_on_sound',
                                    'switch_off.ogg': 'switch_off_sound'}

            style = ember.style.ToggleStyle
            
        elif element == "slider":
            if assets:
                valid_file_names = {'base.png': 'base_image',
                                    'default.png': 'default_image',
                                    'hover.png': 'hover_image',
                                    'click.png': 'click_image',
                                    'focus.png': 'focus_image',
                                    'focus_click.png': 'focus_click_image'}
            
            style = ember.style.SliderStyle

        elif element == "list":
            style = ember.style.ListStyle

        elif element == "text":
            style = ember.style.TextStyle

        elif element == "scroll":
            style = ember.style.ScrollStyle

        else:
            raise ValueError(f"No element matching the name '{element}'.")

        if assets:
            for file in assets:
                if (k := valid_file_names.get(file)):
                    path = os.path.join(asset_path,name,file)
                    if file.endswith(".png") and file != "text_fade.png":
                        kwargs[k] = ember.material.StretchedSurface(path, edge=data.get("image_edge"))
                    else:
                        kwargs[k] = path

        for k, v in value.items():
            if type(v) is list and v[0] in {"COL", "AVG_COL", "STYLE", "FADE", "SURFACE_FADE",
                                            "SLIDE", "PIXEL_FONT", "FONT"}:
                if v[0] == "COL":
                    v = ember.material.Color(v[1])
                elif v[0] == "AVG_COL":
                    v = ember.material.AverageColor(hsv_adjustment=v[1])
                elif v[0] == "STYLE":
                    v = styles[v[1]]
                elif v[0] == "FADE":
                    v = ember.transition.Fade(duration=v[1])
                elif v[0] == "SURFACE_FADE":
                    v = ember.transition.SurfaceFade(duration=v[1])
                elif v[0] == "SLIDE":
                    v = ember.transition.Slide(duration=v[1], direction=v[2])
                elif v[0] == "PIXEL_FONT":
                    v = ember.font.PixelFont(filename=_c.package.joinpath(f'fonts/{v[1]}'))
                elif v[0] == "FONT":
                    v = ember.font.Font(pygame.font.SysFont(v[1], v[2]))
            kwargs[k] = v

        style = style(**kwargs)
        if set_as_default and element == name:
            style.set_as_default()

        styles[name] = style

    if "constants" in data.keys():
        styles.update(data["constants"])
    return styles
