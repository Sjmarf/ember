import pygame
from typing import Union, Optional, Sequence, NoReturn

from .. import common as _c
from ..event import BUTTONCLICKED, ELEMENTFOCUSED

from ..ui.view import View
from ..ui.h_stack import HStack
from ..ui.text import Text
from ..ui.ui_object import Interactive
from ..ui.element import Element, ElementStrType
from ..ui.load_element import load_element

from ..size import SizeType, SequenceSizeType

from ..style.button_style import ButtonStyle
from ..style.load_style import load as load_style

from ..material.material import MaterialController

class Button(Element, Interactive):
    def __init__(self,
                 *element: Union[Sequence[ElementStrType], ElementStrType],
                 size: SequenceSizeType = None,
                 width: SizeType = None,
                 height: SizeType = None,

                 style: Optional[ButtonStyle] = None,

                 disabled: bool = False,
                 can_hold: bool = False,
                 hold_delay: float = 0.2,
                 hold_start_delay: float = 0.5,
                 focus_when_clicked: bool = False
                 ):
        """
        :param element:
        :param size:
        :param width:
        :param height:
        :param style:
        :param disabled:
        :param can_hold:
        :param hold_delay:
        :param hold_start_delay:
        :param focus_when_clicked:
        """

        self.can_hold: bool = can_hold
        """
        If :code:`True`, the button will repeatedly post the :code:`BUTTONCLICKED` event every x 
        seconds whilst the button is held down.
        """

        self.hold_delay: float = hold_delay
        """
        The delay (in seconds) between posting events, if the :code:`can_hold` attribute is :code:`True`.
        """

        self.hold_start_delay: float = hold_start_delay
        """
        The delay (in seconds) between the initial event and the first repeated event, 
        if the :code:`can_hold` attribute is :code:`True`.
        """

        self.focus_when_clicked: bool = focus_when_clicked
        """
        If :code:`True`, the button will be focused when it is clicked.
        """

        self.is_hovered: bool = False
        """
        Is :code:`True` when the mouse is hovered over the button. Read-only.
        """

        self.is_clicked: bool = False
        """
        Is :code:`True` when the button is clicked down. Read-only.
        """

        self.material_controller: MaterialController = MaterialController(self)
        """
        The :ref:`MaterialController<material-controller>` object responsible for managing the Button's materials.
        """

        self._fit_width: float = 0
        self._fit_height: float = 0
        self._hold_timer: float = hold_start_delay
        self._is_held: bool = False

        self._element: Optional[Element] = None

        self.set_style(style)

        super().__init__(size, width, height, default_size=self.style.default_size)
        self.set_element(*element)

        self._disabled: bool = disabled

    def __repr__(self):
        return f"<Button({self._element})>"

    def _set_root(self, root: View) -> NoReturn:
        self.root = root
        if self._element:
            self._element._set_root(root)

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:

        super()._update_rect_chain_down(surface, pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

        w = self.get_abs_width(max_size[0])
        h = self.get_abs_height(max_size[1])
        if self._element:
            self._element._update_rect_chain_down(
                surface,
                (pos[0] + w / 2 - self._element.get_abs_width(w) / 2,
                 pos[1] + h / 2 - self._element.get_abs_height(h) / 2),
                self.rect.size, root)

    def _update_rect_chain_up(self) -> NoReturn:
        if self._width.mode == 1:
            if self._element:
                if self._element._width.mode == 2:
                    raise ValueError("Cannot have elements of FILL width inside of a FIT width Button.")
                self._fit_width = self._element.get_abs_width()
            else:
                self._fit_width = self._style.default_size[0]

        if self._height.mode == 1:
            if self._element:
                if self._element._height.mode == 2:
                    raise ValueError("Cannot have elements of FILL height inside of a FIT height Button.")
                self._fit_height = self._element.get_abs_width()
            else:
                self._fit_height = self._style.default_size[1]

        if self.parent:
            self.parent._update_rect_chain_up()
            self.root.check_size = True

    def _update(self, root: View) -> NoReturn:
        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        # If button is held down, perform action every x seconds
        if self.can_hold and not self._disabled:
            if self.is_clicked:
                self._hold_timer -= _c.delta_time
                if self._hold_timer < 0:
                    self._is_held = True
                    self._hold_timer = self.hold_delay

                    if _c.audio_enabled and not _c.audio_muted:
                        if (s := self._style.click_down_sound) is not None:
                            s.play()
                    self._perform_event()

            else:
                self._hold_timer = self.hold_start_delay

        if self._element:
            self._element._update_a(root)

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255) -> NoReturn:
        # Decide which image to draw
        rect = self.rect.move(*offset)
        if self._disabled:
            material = self.style.disabled_material
        elif self.is_clicked:
            material = self.style.focus_click_material if root.element_focused is self else self.style.click_material
        elif root.element_focused is self:
            material = self.style.focus_material
        elif self.is_hovered:
            material = self.style.hover_material
        else:
            material = self.style.material

        self.material_controller.set_material(material, transition=self._style.material_transition)
        self.material_controller.render(self, surface,
                                        (rect.x - surface.get_abs_offset()[0],
                                         rect.y - surface.get_abs_offset()[1]),
                                        rect.size, alpha)

        if self._element:
            if self.is_clicked:
                offset2 = self._style.element_clicked_offset
            elif root.element_focused is self:
                offset2 = self._style.element_highlight_offset
            elif self.is_hovered:
                offset2 = self._style.element_hover_offset
            else:
                offset2 = self._style.element_offset

            self._element._render_a(surface, (offset[0] + offset2[0], offset[1] + offset2[1]), root, alpha=alpha)

    def _event(self, event: pygame.event.Event, root: View) -> NoReturn:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self._disabled:
            self.is_clicked = self.is_hovered
            if self.is_clicked:
                self._click_down()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered and self.is_clicked and not self._disabled:
                self._click_up()
                if self.focus_when_clicked:
                    root.element_focused = self
                    event = pygame.event.Event(ELEMENTFOCUSED, element=self)
                    pygame.event.post(event)
            self.is_clicked = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and root.element_focused is self \
                and not self._disabled:
            self.is_clicked = True
            self._click_down()

        elif event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            if root.element_focused is self and not self._disabled and self.is_clicked:
                self._click_up()
            self.is_clicked = False

        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0 and root.element_focused is self \
                and not self._disabled:
            self.is_clicked = True
            self._click_down()

        elif event.type == pygame.JOYBUTTONUP and event.button == 0:
            if root.element_focused is self and not self._disabled:
                self._click_up()
            self.is_clicked = False

    def _click_down(self):
        if _c.audio_enabled and not _c.audio_muted:
            if (s := self._style.click_down_sound) is not None:
                s.play()

    def _click_up(self):
        if _c.audio_enabled and not _c.audio_muted:
            if (s := self._style.click_up_sound) is not None:
                if (s2 := self._style.click_down_sound) is not None:
                    s2.stop()
                s.play()
        if self.can_hold:
            if self._is_held:
                self._is_held = False
            else:
                self._perform_event()
        else:
            self._perform_event()

    def _perform_event(self):
        text = self._element.text if isinstance(self._element, Text) else None
        event = pygame.event.Event(BUTTONCLICKED, element=self, text=text)
        pygame.event.post(event)

    def set_disabled(self, value: bool) -> NoReturn:
        self._disabled = value
        self.selectable = not value
        if hasattr(self.parent, "update_rect_chain_up"):
            self.parent._update_rect_chain_up()
        if self._disabled:
            if self.root:
                if self.root.element_focused is self:
                    self.root.element_focused = None

    def _set_style(self, style: Optional[ButtonStyle]) -> NoReturn:
        self.set_style(style)

    def set_style(self, style: Optional[ButtonStyle]) -> NoReturn:
        """
        Sets the ButtonStyle of the Button.
        """
        if style is None:
            if _c.default_button_style is None:
                load_style(_c.DEFAULT_STYLE, parts=['button'])
            self._style: ButtonStyle = _c.default_button_style
        else:
            self._style: ButtonStyle = style

    def _set_element(self, *element: Union[Sequence[ElementStrType], ElementStrType]) -> NoReturn:
        self.set_element(element)

    def set_element(self, *element: Union[Sequence[ElementStrType], ElementStrType]) -> NoReturn:
        """
        Replace the child element of the Button.
        """
        if not element or element == (None,):
            self._element = None

        else:
            if len(element) > 1:
                self._element: Optional[Element] = \
                    HStack(*[load_element(i, text_style=self._style.text_style) for i in element])

            elif isinstance(element[0], (Element, str)):
                self._element: Optional[Element] = load_element(element[0], text_style=self._style.text_style)
            else:
                self._element: Optional[Element] = \
                    HStack(*[load_element(i, text_style=self._style.text_style) for i in element[0]])

            self._element._set_parent(self)

        self._update_rect_chain_up()

    element: Optional[Element] = property(
        fget=lambda self: self._element,
        fset=_set_element,
        doc="The child element of the Button. Synonymous with the set_element() method."
    )

    style: ButtonStyle = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ButtonStyle of the Button. Synonymous with the set_style() method."
    )
