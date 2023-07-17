import abc
from typing import TYPE_CHECKING, Type, Sequence
from copy import copy

from ..size import SizeType, SequenceSizeType, AbsoluteSize
from .. import common as _c

if TYPE_CHECKING:
    from ..ui.base.element import Element


class Style(abc.ABC):
    """
    All Styles inherit from this class. This base class should not be directly instantiated.
    """

    _ELEMENT = None
    _SECONDARY_ELEMENTS = []

    @staticmethod
    def load_size(
        size: SequenceSizeType, width: SizeType, height: SizeType, raise_error=True
    ) -> tuple[AbsoluteSize, AbsoluteSize]:
        w, h = None, None

        if size is not None:
            if isinstance(size, Sequence):
                w, h = size
            else:
                w, h = size, size

        if width is not None:
            w = width
        if height is not None:
            h = height

        if raise_error:
            if w is None:
                raise ValueError("No width was specified.")
            if h is None:
                raise ValueError("No height was specified.")

        return (
            AbsoluteSize(w) if isinstance(w, (int, float)) else w,
            AbsoluteSize(h) if isinstance(h, (int, float)) else h,
        )

    def copy(self) -> "Style":
        return copy(self)

    def set_as_default(self, *classes: Type["Element"]) -> "Style":
        if classes:
            for cls in classes:
                if not (
                    issubclass(cls, self._ELEMENT)
                    or any(issubclass(cls, i) for i in self._SECONDARY_ELEMENTS)
                ):
                    raise ValueError(
                        f"{cls.__name__} needs to be a subclass of {self._ELEMENT.__name__}."
                    )
                _c.default_styles[cls] = self
        else:
            _c.default_styles[self._ELEMENT] = self
        return self


