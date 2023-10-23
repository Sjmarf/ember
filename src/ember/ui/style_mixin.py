import inspect
import pygame
import itertools
from typing import Optional, TYPE_CHECKING, Union, Iterable
from collections import OrderedDict
from ember.ui.base.element import Element

from ember import common as _c
from ember.common import DEFAULT, DefaultType

from ember.trait.trait import Trait

if TYPE_CHECKING:

    from ember.style.state import State

StyleType = Union["Style", DefaultType, Iterable["Style"]]

class Style(Element):
    def __init__(self, *args, style: Optional[StyleType] = DEFAULT, **kwargs):
        super().__init__(*args, **kwargs)

        self._style_input = style
        self._styles: OrderedDict[Optional["Style"], list["State"]] = OrderedDict(
            [(None, [])]
        )

    def _build(self) -> None:
        if self._style_input is DEFAULT:
            for cls in inspect.getmro(type(self)):
                if cls in _c.default_styles:
                    self.add_style(_c.default_styles[cls])
                    break

        elif isinstance(self._style_input, Iterable):
            for i in self._style_input:
                self.add_style(i)

        elif self._style_input is not None:
            self.add_style(self._style_input)

        with Trait.inspecting(Trait.Layer.STYLE):
            for state in itertools.chain(*self._styles.values()):
                if state.on_become_active_callable is not None:
                    state.on_become_active_callable(self)

        del self._style_input
        super()._build()

    def _post_event(self, event: pygame.event.Event) -> None:
        pygame.event.post(event)
        with Trait.inspecting(Trait.Layer.STYLE):
            for style in self._styles:
                if style is not None:
                    style.process_event(self, event)

    def set_style(self, style: "Style") -> None:
        """
        Replace the Element Style.
        """
        if self._styles:
            self.remove_style(next(reversed(self._styles)))
        self.add_style(style)

    def add_style(self, style: "Style") -> None:
        """
        Add a Style to the Element.
        """
        if style in self._styles:
            return
        with Trait.inspecting(Trait.Layer.STYLE):
            self._styles[style] = []
            style.activate(self)

    def remove_style(self, style: "Style") -> None:
        """
        Remove a Style from the Element.
        """
        if style not in self._styles:
            return
        with Trait.inspecting(Trait.Layer.STYLE):
            del self._styles[style]
            style.deactivate(self)
