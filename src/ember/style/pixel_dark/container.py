from abc import ABC

from ember.base.container import Container as _Container
from .text import Text


class Container(_Container, ABC):
    text_class = Text
