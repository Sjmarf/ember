import pygame
import inspect
from typing import Optional, Union, Sequence, TYPE_CHECKING
from .element import Element

from ...size import SizeType, SequenceSizeType, OptionalSequenceSizeType
from ...position import PositionType, SequencePositionType

from ... import common as _c

if TYPE_CHECKING:
    from ...style.style import Style

class StyleMixin(Element):
    def __init__(
        self,
        *args,
        style: Optional["Style"] = None,
        **kwargs
    ):
        self.set_style(style)
        super().__init__(*args, **kwargs)

    def _get_style(self, style: Optional["Style"], *classes):
        """
        Used interally by the library.
        """
        if style is None:
            for cls in classes if classes else inspect.getmro(type(self)):
                if cls in _c.default_styles:
                    return _c.default_styles[cls]
            raise _c.Error(
                f"Tried to find a style for {type(self).__name__}, but no style was found."
            )
        else:
            return style

    @property
    def style(self) -> "Style":
        """
        Get or set the Style of the Element. If you specify None when setting the style, the default Style will be applied.
        The property setter is synonymous with the :py:meth:`set_style<ember.ui.base.Element.set_style>` method.
        """
        return self._style

    @style.setter
    def style(self, style: "Style") -> None:
        self.set_style(style)

    def set_style(self, style: "Style") -> None:
        """
        Set the style of the Container.
        """
        self._style: "Style" = self._get_style(style)