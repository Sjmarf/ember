from enum import Enum


class TraitLayer(Enum):
    ANIMATION = 0
    ELEMENT = 1
    PARENT = 2
    DEFAULT = 3


inspected = TraitLayer.ELEMENT
