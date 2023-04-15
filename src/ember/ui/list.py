import abc
from .. import common as _c
from typing import Union, Optional, NoReturn

from .view import View
from .. import log

from .element import Element
from ..style.load_style import load as load_style

from ..style.list_style import ListStyle

from ..utility.timer import BasicTimer

class List(abc.ABC):
    def __init__(self, list_style, row_selected):
        self.root: Optional[View] = None
        self.parent: Union[Element, View, None] = None
        self._elements: list[Element] = []

        self.set_list_style(list_style)

        self.selected: Optional[Element] = row_selected
        self._defer_selection: bool = True
        self.sel_pos_anim: BasicTimer = BasicTimer(0)
        self.sel_size_anim: BasicTimer = BasicTimer(0)

    def _update(self, root: View) -> NoReturn:

        if not self._elements:
            return

        if root.element_focused in self.elements:
            if self.selected is not root.element_focused:
                self.set_selected(root.element_focused)

        self.sel_pos_anim.tick()
        self.sel_size_anim.tick()

        [i._update_a(root) for i in self._elements]

    def _set_list_style(self, style: ListStyle) -> NoReturn:
        self.set_list_style(style)

    @abc.abstractmethod
    def set_selected(self, element: Union[int, Element]) -> NoReturn:
        """
        Set which element is currently selected.
        """
        pass

    def set_list_style(self, style: ListStyle) -> NoReturn:
        """
        Set the ListStyle of the Stack.
        """
        if style is None:
            if _c.default_list_style is None:
                load_style(_c.DEFAULT_STYLE, parts=['list'])
            self._list_style: ListStyle = _c.default_list_style
        else:
            self._list_style: ListStyle = style

    def _enter_in_first_element(self, root: View, key: str, ignore_self_focus: bool = False) -> Optional[Element]:
        if self.focus_self and not ignore_self_focus:
            log.nav.info(self, "Returning self.")
            return self

        if self.selected:
            log.nav.info(self, f"-> child {self.selected}.")
            return self.selected._focus_chain(root, None, direction=key)

    list_style = property(
        fget=lambda self: self._list_style,
        fset=_set_list_style,
        doc=":getter: Returns the ListStyle applied to the List.\n"
            ":setter: Sets the ListStyle of the stack. Synonymous with the set_list_style() method.\n"
            ":type: :code:`ember.style.ListStyle`"
    )
