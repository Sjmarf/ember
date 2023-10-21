import abc
from typing import Optional, Union, Sequence
from abc import ABC, abstractmethod
import pygame

from ember.axis import Axis, HORIZONTAL, VERTICAL

from ..material import Material
from ..material.blank import Blank

from .. import common as _c

from ..event import TOGGLEDON, TOGGLEDOFF

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

from ember.base.element import Element
from ember.base.can_pivot import CanPivot
from .interactive_gauge import InteractiveGauge
from .bar import Bar
from .panel import Panel
from ..common import MaterialType, SequenceElementType
from ..utility.load_material import load_material

from ..on_event import on_event


class Slider(InteractiveGauge, Bar, ABC):
    ...