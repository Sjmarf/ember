import pygame
from typing import Union, Optional, TYPE_CHECKING, Sequence, NoReturn
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


from .. import common as _c
from ..event import TEXTFIELDCLOSED, TEXTFIELDMODIFIED
from .element import Element
from .text import Text
from .v_scroll import VScroll
from .h_scroll import HScroll
from .scroll import Scroll
from .ui_object import Interactive
from ..style.text_field_style import TextFieldStyle
from ..style.load_style import load as load_style

from ..size import SizeType, SequenceSizeType, FILL, FIT

from ..material.material import MaterialController

if TYPE_CHECKING:
    from .view import View

# Contains sus characters
EXCLUDED_CHARS = ['']


class TextField(Element, Interactive):
    def __init__(self,
                 text: Union[str, Text] = "",
                 size: SequenceSizeType = None,
                 width: SizeType = None,
                 height: SizeType = None,
                 style: Optional[TextFieldStyle] = None,

                 prompt: Union[str, Text, None] = None,
                 disabled: bool = False,
                 hide_input: bool = False,
                 max_length: Optional[int] = None,
                 allowed_characters: Union[str, Sequence[str], None] = None,
                 multiline: bool = False
                 ):

        self.hide_input: bool = hide_input
        """
        When :code:`True`, letters will be replaced with bullet points (•), as in a password input.
        """

        self.max_length: Optional[int] = max_length
        """
        The maximum length of the text. If set to :code:`None`, no limit is applied.
        """

        self.allowed_characters: Union[str, Sequence[str], None] = allowed_characters
        """
        A sequence or string of allowed characters. If set to :code:`None`, all characters will be allowed.
        """

        self.is_hovered: bool = False
        """
        Is :code:`True` when the mouse is hovered over the TextField. Read-only.
        """

        self.is_active: bool = False
        """
        Is :code:`True` when the TextField is open. Read-only.
        """

        self.material_controller: MaterialController = MaterialController(self)
        """
        The :ref:`MaterialController<material-controller>` object responsible for managing the TextField's materials.
        """

        self._multiline: bool = multiline

        self._repeating_key: Optional[int] = None

        self._cursor_timer: int = 0

        self._cursor_x: int = 0
        self._cursor_index: int = 0
        self._cursor_line: int = 0

        self._highlight_x: int = 0
        self._highlight_index: int = 0
        self._highlight_line: int = 0

        self._highlighting: bool = False
        self._highlighted: bool = False

        self.set_style(style)

        self._repeated_key_timer: float = self._style.key_repeat_start_delay

        # If a str is passed as the element, convert to a Text object.
        if self._multiline:
            text_style = text.style if isinstance(text, Text) else _c.default_text_style
            element_size = (FILL - text_style.font.cursor.get_width() * 2, FIT)
        else:
            element_size = (FIT, FIT)

        if isinstance(text, str):
            self._text_element: Text = Text(text, color=self._style.text_color, size=element_size, align="left")
        else:
            self._text_element: Text = text
            text.set_size(element_size)

        self._text_element._set_parent(self)

        if isinstance(prompt, str):
            self._prompt: Text = Text(prompt, color=self._style.text_color, size=element_size)
        else:
            self._prompt: Text = prompt
            if prompt:
                prompt.set_size(element_size)

        if self._prompt:
            self._prompt._set_parent(self)

        if self._multiline:
            self._scroll: Scroll = VScroll(self._text_element, size=self._style.default_scroll_size)
        else:
            self._scroll: Scroll = HScroll(self._text_element, size=self._style.default_scroll_size,
                                           over_scroll=[self._text_element._style.font.cursor.get_width()] * 2)

        self._scroll_offset = (0, 0)

        self._update_text(self._text_element.text)

        if max_length is not None and len(self._text) > self.max_length:
            raise ValueError(f"Text length ({len(self._text)}) is greater than max_length {self.max_length}.")

        super().__init__(size, width, height, default_size=self._style.default_size)
        self._disabled: bool = disabled

    def __repr__(self):
        return f"TextField({self._text_element})"

    def _on_unfocus(self) -> NoReturn:
        if self.is_active:
            self._deselect(self.root)

    def _set_root(self, root: "View") -> NoReturn:
        self.root = root
        self._text_element._set_root(root)
        if self._prompt:
            self._prompt._set_root(root)

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:

        super()._update_rect_chain_down(surface, pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

        pos = (pos[0] + self.rect.w / 2 - self._scroll.get_abs_width(self.rect.w) / 2,
               pos[1] + self.rect.h / 2 - self._scroll.get_abs_height(self.rect.h) / 2)
        self._scroll._update_rect_chain_down(surface, pos, self.get_abs_size(max_size), root)

        if self.is_active:
            self._update_cursor_pos(reset_timer=False, mode="cursor")
            self._update_cursor_pos(reset_timer=False, mode="highlight")

        if self._prompt is not None:
            self._prompt._update_rect_chain_down(
                surface,
                (0, self.rect.h // 2 - self._prompt.get_abs_height(self.rect.h) // 2),
                (self.rect.w, self.rect.y), root)

    def _update(self, root: "View") -> NoReturn:
        # If the backspace key is held, repeat multiple times
        if self.is_active:

            if self._repeating_key:
                keys = pygame.key.get_pressed()
                if keys[self._repeating_key]:
                    self._repeated_key_timer -= _c.delta_time
                    if self._repeated_key_timer <= 0:
                        self._repeated_key_timer = self._style.key_repeat_delay
                        self._run_keypress(self._repeating_key)
            else:
                self._repeated_key_timer = self._style.key_repeat_start_delay

        if self._highlighting:
            if not self._scroll.scroll.playing:
                if self._multiline:
                    self._scroll.scroll_to_show_position(_c.mouse_pos[1], size=self._line_height)
                else:
                    self._scroll.scroll_to_show_position(_c.mouse_pos[0], size=self._line_height)

        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        # self._text_element.update(root)

        self._scroll._update(root)

        if self._prompt is not None:
            self._prompt._update(root)

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View",
                alpha: int = 255, _ignore_fill_width=False, _ignore_fill_height=False):
        rect = self.rect.move(*offset)
        # Decide which background image to draw
        if self._disabled:
            material = self._style.disabled_material
        elif root.element_focused is self:
            material = self._style.active_material
        elif self.is_hovered:
            material = self._style.hover_material
        else:
            material = self._style.material

        self.material_controller.set_material(material, transition=self._style.material_transition)
        self.material_controller.render(self, surface, rect.topleft, rect.size, alpha)

        if self._text:
            # Draw highlight
            if self.is_active:
                if (self._highlighted or self._highlighting) and self._scroll.subsurf:
                    if self._highlighting:
                        if (result := self._get_position_of_click()) is not None:
                            self._highlight_index = result[0]
                            self._update_cursor_pos(line_index=result[1], mode="highlight")

                        if self._highlight_index != self._cursor_index:
                            # If the position of the click-up is not the same as the position of the click-down,
                            # the user is trying to highlight
                            (_, start_x, start_line), (_, end_x, end_line) = \
                                sorted(((self._cursor_index, self._cursor_x, self._cursor_line),
                                        (self._highlight_index, self._highlight_x, self._highlight_line)),
                                       key=lambda x: x[0])
                        else:
                            # This is just to keep Pycharm QA happy
                            start_line, end_line, start_x, end_x = None, None, 0, 0
                    else:
                        start_x, start_line = self._cursor_x, self._cursor_line
                        end_x, end_line = self._highlight_x, self._highlight_line

                    if self._highlight_index != self._cursor_index:
                        start_line = self._text_element.get_line(start_line)
                        end_line = self._text_element.get_line(end_line)

                        scroll_offset = self._scroll.subsurf.get_abs_offset()
                        scroll_offset = (self._text_element.rect.x - scroll_offset[0],
                                         self._text_element.rect.y - scroll_offset[1])

                        if self._cursor_line == self._highlight_line:
                            y = start_line.line_index * self._line_height + \
                                self._text_element._style.font.cursor_offset[1] + scroll_offset[1]

                            pygame.draw.rect(self._scroll.subsurf,
                                             self._style.highlight_color,
                                             (start_x + scroll_offset[0] +
                                              self._text_element._style.font.cursor_offset[0], y,
                                              end_x - start_x,
                                              self._text_element._style.font.cursor.get_height()))
                        else:
                            # Top line
                            y = start_line.line_index * self._line_height + \
                                self._text_element._style.font.cursor_offset[1] + scroll_offset[1]
                            pygame.draw.rect(self._scroll.subsurf,
                                             self._style.highlight_color,
                                             (start_x + scroll_offset[0] +
                                              self._text_element._style.font.cursor_offset[0], y,
                                              start_line.width - start_x + start_line.start_x,
                                              self._text_element._style.font.cursor.get_height()))

                            # Middle lines
                            for line_index in range(start_line.line_index + 1, end_line.line_index):
                                line = self._text_element.get_line(line_index)
                                y = line.line_index * self._line_height + \
                                    self._text_element._style.font.cursor_offset[1] + scroll_offset[1]
                                pygame.draw.rect(self._scroll.subsurf,
                                                 self._style.highlight_color,
                                                 (line.start_x + scroll_offset[0] +
                                                  self._text_element._style.font.cursor_offset[0], y, line.width,
                                                  self._text_element._style.font.cursor.get_height()))

                            # Bottom line
                            y = end_line.line_index * self._line_height + \
                                self._text_element._style.font.cursor_offset[1] + scroll_offset[1]
                            pygame.draw.rect(self._scroll.subsurf,
                                             self._style.highlight_color,
                                             (end_line.start_x + scroll_offset[0] +
                                              self._text_element._style.font.cursor_offset[0], y,
                                              end_x - end_line.start_x,
                                              self._text_element._style.font.cursor.get_height()))

            self._scroll._render_a(surface, offset, root, alpha=alpha)

        # Draw cursor
        if self.is_active:

            if not (self._highlighting or self._highlighted):
                self._cursor_timer += _c.delta_time
                if self._cursor_timer < self._style.cursor_blink_speed:
                    cursor_x = self._text_element.rect.x + self._cursor_x + \
                               self._text_element._style.font.cursor_offset[0]

                    cursor = self._text_element._style.font.cursor.copy()
                    cursor.fill(self._style.cursor_color, special_flags=pygame.BLEND_RGB_ADD)

                    cursor_y = self._text_element.rect.y + self._text_element._style.font.cursor_offset[1] + \
                               self._cursor_line * self._line_height - \
                               self._scroll.subsurf.get_abs_offset()[1]

                    self._scroll.subsurf.blit(cursor, (cursor_x - self._scroll.subsurf.get_abs_offset()[0], cursor_y))
                if self._cursor_timer > self._style.cursor_blink_speed * 2:
                    self._cursor_timer = 0

    def _deselect(self, root):
        if root.element_focused is self:
            root.element_focused = None
        if self.is_active:
            self.is_active = False
            event = pygame.event.Event(TEXTFIELDCLOSED, element=self, text=self._text)
            pygame.event.post(event)

    def _update_text(self, text):
        self._text = text
        self._text_element.set_text("•" * len(text) if self.hide_input else text)
        self._cursor_timer = 0
        event = pygame.event.Event(TEXTFIELDMODIFIED, element=self, text=text)
        pygame.event.post(event)

    def _get_position_of_click(self):
        y = _c.mouse_pos[1] - self._text_element.rect.y - self._text_element._style.font.cursor_offset[1]
        line_index = int(y) // (
                    self._text_element._style.font.line_height + self._text_element._style.font.line_spacing)

        line_index = min(max(0, line_index), len(self._text_element.lines) - 1)
        line = self._text_element.get_line(line_index)
        if line is None:
            return None
        target_x = _c.mouse_pos[0] - self._text_element.rect.x - line.start_x

        prev_x = 0
        for n in range(len(line.content)):
            if (current_x := self._text_element._style.font.get_width_of(line.content[:n])) > target_x:
                result = line.start_index + n
                if abs(target_x - prev_x) < abs(target_x - current_x):
                    result -= 1
                return result, line_index
            prev_x = current_x

        return line.start_index + len(line.content), line_index

    def _set_cursor_to_end(self):
        self._cursor_index = len(self._text_element.text)
        self._update_cursor_pos()
        self._cursor_timer = 0
        self._highlighting = False
        self._highlighted = False

    def _update_cursor_pos(self, line_index=None, reset_timer=True, mode: Literal["cursor", "highlight"] = "cursor"):
        index = self._cursor_index if mode == "cursor" else self._highlight_index
        if line_index is None:
            line_index = self._text_element.get_line_index_from_letter_index(index)
        line = self._text_element.get_line(line_index)

        x = line.start_x + \
            self._text_element._style.font.get_width_of(line.content[:index - line.start_index])
        if mode == "cursor":
            self._cursor_x = x
            self._cursor_line = line_index
            if reset_timer:
                self._cursor_timer = 0
        else:
            self._highlight_x = x
            self._highlight_line = line_index

        if mode == "cursor":
            if not self._scroll.scroll.playing:
                self._text_element._check_for_surface_update()
                self._scroll._scrollbar_calc()
                if self._multiline:
                    self._scroll.scroll_to_show_position(
                        self._text_element.rect.y + self._cursor_line * self._line_height,
                        size=self._line_height, duration=0)
                else:
                    self._scroll.scroll_to_show_position(self._text_element.rect.x + self._cursor_x,
                                                         size=self._text_element._style.font.cursor.get_width(),
                                                         offset=3, duration=0)

    def _remove_highlighted_area(self):
        new_text = self._text[:self._cursor_index] + self._text[self._highlight_index - 1:]

        if self._highlighted:
            self._highlighted = False
            self._update_text(new_text)
            return True
        return False

    def _backspace(self):
        if not self._remove_highlighted_area() and self._cursor_index != 0:
            self._cursor_index -= 1

        self._update_text(self._text[:self._cursor_index] + self._text[self._cursor_index + 1:])
        self._update_cursor_pos(line_index=None if self._text else 0)

    def _up_down_line(self, direction: int):
        if self._cursor_line != (len(self._text_element.lines) - 1 if direction == 1 else 0):
            line = self._text_element.get_line(self._cursor_line + direction)
            target = self._cursor_x
            output = len(line)
            for i in range(len(line)):
                w = line.start_x + self._text_element._style.font.get_width_of(line.content[:i])
                if w >= target:
                    if i == 0:
                        output = 0
                    else:
                        w2 = line.start_x + self._text_element._style.font.get_width_of(line.content[:i - 1])
                        if abs(w2 - target) < abs(w - target):
                            output = i - 1
                        else:
                            output = i

                    break

            self._cursor_index = line.start_index + output
            self._update_cursor_pos(line_index=self._cursor_line + direction)

    def _run_keypress(self, key):
        if key == pygame.K_LEFT:
            if self._cursor_index != 0 and not self._highlighted:
                self._cursor_index -= 1
                self._update_cursor_pos()
            return True

        elif key == pygame.K_RIGHT:
            if self._cursor_index != len(self._text_element.text) and not self._highlighted:
                self._cursor_index += 1
                self._update_cursor_pos()
            return True

        elif key == pygame.K_DOWN:
            self._up_down_line(1)
            return True

        elif key == pygame.K_UP:
            self._up_down_line(-1)
            return True

        elif key == pygame.K_BACKSPACE:
            self._backspace()
            return True

    def _event(self, event: pygame.event.Event, root: "View"):
        if self._disabled:
            return

        if self._scroll._event(event, root):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.is_active:
                self._highlighting = True
                if (result := self._get_position_of_click()) is not None:
                    self._cursor_index = result[0]
                    self._update_cursor_pos(line_index=result[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered or self._highlighting:
                if self.is_active:
                    # If the position of the click-up is not the same as the position of the click-down,
                    # the user is trying to highlight
                    if self._text:
                        if self._highlighting:
                            self._highlighted = self._cursor_index != self._highlight_index
                            if self._highlighted:
                                (self._cursor_index, self._cursor_line, self._cursor_x), \
                                (self._highlight_index, self._highlight_line, self._highlight_x) = \
                                    sorted(((self._cursor_index, self._cursor_line, self._cursor_x),
                                            (self._highlight_index, self._highlight_line, self._highlight_x)),
                                           key=lambda x: x[0])
                        self._cursor_timer = 0
                else:
                    self.is_active = True
                    if root.element_focused is not self and isinstance(root.element_focused, TextField):
                        root.element_focused.is_active = False
                    root.element_focused = self
                    if (result := self._get_position_of_click()) is not None:
                        self._cursor_index = result[0]
                        self._update_cursor_pos(line_index=result[1])

            elif self.is_active:
                self._deselect(root)

            self._highlighting = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN and root.element_focused is self:
                if not self.is_active:
                    self.is_active = True
                    self._set_cursor_to_end()

            elif event.key == self._repeating_key:
                self._repeating_key = None

        elif event.type == pygame.KEYDOWN and self.is_active:
            mods = pygame.key.get_mods()
            if self._run_keypress(event.key):
                self._repeating_key = event.key
                self._repeated_key_timer = self._style.key_repeat_start_delay
                return

            if event.key == pygame.K_ESCAPE:
                self._deselect(root)

            elif event.key == pygame.K_RETURN and not self._multiline:
                self._deselect(root)

            elif mods & pygame.KMOD_META or mods & pygame.KMOD_LCTRL or mods & pygame.KMOD_RCTRL:
                if event.key == pygame.K_a:
                    self._highlighted = True
                    self._cursor_index = 0
                    self._highlight_index = len(self._text_element.text) + 1
                    self._update_cursor_pos(mode='cursor')
                    self._update_cursor_pos(mode='highlight')

                elif event.key == pygame.K_c:
                    data = self._text[self._cursor_index:self._highlight_index]
                    if _c.is_ce and pygame.vernum[0] > 2 and pygame.vernum[1] > 2:
                        pygame.scrap.put_text(data)
                    else:
                        # This can be removed if we drop support for < CE 2.2.0
                        pygame.scrap.put("text/plain;charset=utf-8", data.encode(encoding='UTF-8'))

                elif event.key == pygame.K_v:
                    if _c.is_ce and pygame.vernum[0] > 2 and pygame.vernum[1] > 2:
                        data = pygame.scrap.get_text()
                    else:
                        # This can be removed if we drop support for < CE 2.2.0
                        data = pygame.scrap.get("text/plain;charset=utf-8").decode(encoding='UTF-8')

                    new_text = self._text[:self._cursor_index] + data + self._text[self._cursor_index:]

                    if self.max_length is not None:
                        if len(new_text) >= self.max_length:
                            return

                    self._remove_highlighted_area()
                    self._update_text(new_text)
                    self._cursor_index += len(data)
                    self._update_cursor_pos()

            elif event.key == pygame.K_DELETE:
                if not self._remove_highlighted_area() and self._cursor_index != len(self._text):
                    self._update_cursor_pos()
                    self._update_text(self._text[:self._cursor_index] + self._text[self._cursor_index + 1:])

            else:
                char = "\n" if event.unicode == "\r" else event.unicode
                if char not in EXCLUDED_CHARS and \
                        (self.allowed_characters is None or char in self.allowed_characters):

                    if self.max_length is not None:
                        if len(self._text) >= self.max_length:
                            return
                    self._remove_highlighted_area()

                    self._cursor_index += 1
                    self._update_text(self._text[:self._cursor_index - 1] + char +
                                      self._text[self._cursor_index - 1:])

                    self._update_cursor_pos()

        elif event.type == pygame.JOYBUTTONUP and event.button == 0 and root.element_focused is self:
            self.is_active = not self.is_active

    def _focus_chain(self, root: "View", previous: Element = None, direction: str = 'in'):
        if direction == 'in':
            if type(root.element_focused) is TextField:
                if root.element_focused.is_active:
                    self.is_active = True
                    root.element_focused.is_active = False
                    self._set_cursor_to_end()
            return self
        else:
            return self.parent._focus_chain(root, self, direction=direction)

    def _set_text(self, text: str) -> NoReturn:
        self.set_text(text)

    def set_text(self, text: str) -> NoReturn:
        """
        Set the text on the button.
        """
        self._update_text(text)
        self._update_cursor_pos()

    def set_disabled(self, value: bool):
        self._disabled = value
        self._can_focus = not value
        if hasattr(self.parent, "update_rect_chain_up"):
            self.parent._update_rect_chain_up()
        if self._disabled:
            if self.root:
                self._deselect(self.root)

    def _get_line_height(self):
        return self._text_element._style.font.line_height + self._text_element._style.font.line_spacing

    def _set_style(self, style: Optional[TextFieldStyle]) -> NoReturn:
        self.set_style(style)

    def set_style(self, style: Optional[TextFieldStyle]) -> NoReturn:
        """
        Sets the TextFieldStyle of the TextField.
        """
        if style is None:
            if _c.default_text_field_style is None:
                load_style("plastic", parts=['text_field'])
            self._style: TextFieldStyle = _c.default_text_field_style
        else:
            self._style: TextFieldStyle = style

    def _set_multiline(self, value: Optional[bool] = None) -> NoReturn:
        self.set_multiline(value)

    def set_multiline(self, value: Optional[bool] = None) -> NoReturn:
        """
        If set to :code:`True`, text will wrap onto a second line when it reaches the end of the TextField.
        """
        if value is None:
            value = not self._multiline
        self._multiline = value

        if value:
            self._text_element.set_size(FILL - FILL - self._text_element._style.font.cursor.get_width() * 2, FIT)
            self._scroll = VScroll(self._text_element, size=self._style.default_scroll_size)
        else:
            self._text_element.set_size(FIT, FIT)
            self._scroll = HScroll(self._text_element, size=self._style.default_scroll_size,
                                   over_scroll=[self._text_element._style.font.cursor.get_width()] * 2)

        self._text_element._update_surface()
        self._update_cursor_pos()

    _line_height = property(fget=_get_line_height)

    text = property(
        fget=lambda self: self._text,
        fset=_set_text,
        doc="The text string contained within the TextField."
    )

    style = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The TextFieldStyle of the TextField. Synonymous with the set_style() method."
    )

    multiline = property(
        fget=lambda self: self._multiline,
        fset=_set_multiline,
        doc="If set to :code:`True`, text will wrap onto a second line when it reaches the end of the TextField."
    )
