import pygame
from typing import Union, Optional, TYPE_CHECKING, Literal

from ember import common as _c
import ember.event
from ember.ui.element import Element
from ember.ui.text import Text
from ember.ui.ui_object import Interactive
from ember.style.text_field_style import TextFieldStyle
from ember.style.load_style import load as load_style

from ember.utility.timer import BasicTimer

from ember.material.material import MaterialController

if TYPE_CHECKING:
    from ember.ui.view import View

# Contains sus characters
EXCLUDED_CHARS = ['']


class TextField(Element, Interactive):
    def __init__(self,
                 text: Union[str, Text] = "",
                 size: Optional[tuple[float, float]] = None,
                 width: Optional[float] = None,
                 height: Optional[float] = None,
                 style: Optional[TextFieldStyle] = None,

                 prompt: Union[str, Text, None] = None,
                 disabled: bool = False,
                 hide_input: bool = False,
                 max_length: Optional[int] = None,
                 allowed_characters: Optional[str] = None,
                 multiline: bool = False
                 ):

        self.hide_input = hide_input
        self.max_length = max_length
        self.allowed_characters = allowed_characters
        self.multiline = multiline
        self._disabled = disabled

        self.is_hovered = False
        self.is_active = False
        self._repeating_key = None
        self._text_y = 0

        self.material_controller = MaterialController(self)

        self._cursor_timer = 0

        self._cursor_x = 0
        self._cursor_index = 0
        self._cursor_line = 0

        self._highlight_x = 0
        self._highlight_index = 0
        self._highlight_line = 0

        self._highlighting = False
        self._highlighted = False

        # Load the TextFieldStyle object.
        if style is None:
            if _c.default_text_field_style is None:
                load_style("plastic", parts=['text_field'])
            self.style = _c.default_text_field_style
        else:
            self.style = style

        self._repeated_key_timer = self.style.backspace_start_delay

        # If a str is passed as the element, convert to a Text object.
        if type(text) is str:
            self._text_element = Text(text, color=self.style.text_color, width=ember.FILL)
        else:
            self._text_element = text

        if type(prompt) is str:
            self._prompt = Text(prompt, color=self.style.text_color, width=ember.FILL)
        else:
            self._prompt = prompt

        self._update_text(self._text_element.text)

        # If None is passed as a size value, then use the first set size. If unavailable, use the style image size.
        if size is None:
            if width is not None:
                self.width = width
            else:
                self.width = self.style.images[0].surface.get_width()

            if height is not None:
                self.height = height
            else:
                self.height = self.style.images[0].surface.get_height()
        else:
            self.width, self.height = size

        super().__init__(self.width, self.height)

    def __repr__(self):
        return f"TextField('{self._text}')"

    def unfocus(self):
        if self.is_active:
            self._deselect(self.root)

    def update(self, root: "View"):
        # If the backspace key is held, repeat multiple times
        if self.is_active:

            if self._repeating_key:
                keys = pygame.key.get_pressed()
                if keys[self._repeating_key]:
                    self._repeated_key_timer -= _c.delta_time
                    if self._repeated_key_timer <= 0:
                        self._repeated_key_timer = self.style.backspace_repeat_speed
                        self._run_keypress(self._repeating_key)
            else:
                self._repeated_key_timer = self.style.backspace_start_delay

        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        self._text_y = self.rect.h // 2 - self._text_element.get_height(self.rect.h) // 2

        self._text_element.update_rect((self.style.padding, self._text_y),
                                       (self.rect.w - self.style.padding * 2, self.rect.y), root)
        self._text_element.update(root)

        if self._prompt is not None:
            self._prompt.update_rect((self.style.padding, self.rect.h // 2 - self._prompt.get_height(self.rect.h) // 2),
                                     (self.rect.w - self.style.padding * 2, self.rect.y), root)
            self._prompt.update(root)

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View",
               alpha: int = 255, _ignore_fill_width=False, _ignore_fill_height=False):
        rect = self.rect.move(*offset)
        # Decide which background image to draw
        if self._disabled:
            img_num = 3
        elif root.element_focused is self:
            img_num = 2
        elif self.is_hovered:
            img_num = 1
        else:
            img_num = 0

        self.material_controller.set_material(self.style.images[img_num])
        self.material_controller.render(self, surface, rect.topleft, rect.size, alpha)

        text_surface = pygame.Surface(rect.size, pygame.SRCALPHA)

        if self._text:
            # Draw highlight
            if self.is_active:
                if self._highlighted or self._highlighting:
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

                        if self._cursor_line == self._highlight_line:
                            y = start_line.line_index * self._line_height + self._text_y + \
                                self._text_element.style.font.cursor_offset[1]

                            pygame.draw.rect(text_surface,
                                             self.style.highlight_color,
                                             (
                                             self.style.padding + start_x + self._text_element.style.font.cursor_offset[
                                                 0], y,
                                             end_x - start_x,
                                             self._text_element.style.font.cursor.get_height()))
                        else:
                            # Top line
                            y = start_line.line_index * self._line_height + self._text_y + \
                                self._text_element.style.font.cursor_offset[1]
                            pygame.draw.rect(text_surface,
                                             self.style.highlight_color,
                                             (
                                             self.style.padding + start_x + self._text_element.style.font.cursor_offset[
                                                 0], y,
                                             start_line.width - start_x + start_line.start_x,
                                             self._text_element.style.font.cursor.get_height()))

                            # Middle lines
                            for line_index in range(start_line.line_index + 1, end_line.line_index):
                                line = self._text_element.get_line(line_index)
                                y = line.line_index * self._line_height + self._text_y + \
                                    self._text_element.style.font.cursor_offset[1]
                                pygame.draw.rect(text_surface,
                                                 self.style.highlight_color,
                                                 (self.style.padding + line.start_x +
                                                  self._text_element.style.font.cursor_offset[0], y, line.width,
                                                  self._text_element.style.font.cursor.get_height()))

                            # Bottom line
                            y = end_line.line_index * self._line_height + self._text_y + \
                                self._text_element.style.font.cursor_offset[1]
                            pygame.draw.rect(text_surface,
                                             self.style.highlight_color,
                                             (self.style.padding + end_line.start_x +
                                              self._text_element.style.font.cursor_offset[0], y,
                                              end_x - end_line.start_x,
                                              self._text_element.style.font.cursor.get_height()))

            self._text_element.render_a(text_surface, offset, root, alpha=alpha)
        elif self._prompt is not None:
            self._prompt.render_a(text_surface, offset, root, alpha=alpha)

        surface.blit(text_surface, self.rect.topleft)

        # Draw cursor
        if self.is_active:

            if not (self._highlighting or self._highlighted):
                self._cursor_timer += _c.delta_time
                if self._cursor_timer < self.style.cursor_blink_speed:
                    # sself._update_cursor_pos(reset_timer=False,line_index = self.line_index)
                    if self._text_element.text:
                        cursor_x = self.rect.x + self.style.padding + self._cursor_x
                    else:
                        cursor_x = self.rect.x + (self.style.padding if self.style.text_align == "left"
                                                  else self.rect.w / 2)

                    cursor = self._text_element.style.font.cursor.copy()
                    cursor.fill(self.style.cursor_color, special_flags=pygame.BLEND_RGB_ADD)

                    surface.blit(cursor,
                                 (cursor_x + self._text_element.style.font.cursor_offset[0],
                                  self.rect.y + self._text_y + self._text_element.style.font.cursor_offset[1] +
                                  self._cursor_line * self._line_height))
                if self._cursor_timer > self.style.cursor_blink_speed * 2:
                    self._cursor_timer = 0

    def _deselect(self, root):
        if root.element_focused is self:
            root.element_focused = None
        if self.is_active:
            self.is_active = False
            event = pygame.event.Event(ember.event.TEXTFIELDCLOSED, element=self, text=self._text)
            pygame.event.post(event)

    def _update_text(self, text):
        self._text = text
        self._text_element.set_text("•" * len(text) if self.hide_input else text)
        self._cursor_timer = 0
        event = pygame.event.Event(ember.event.TEXTFIELDMODIFIED, element=self, text=text)
        pygame.event.post(event)

    def _get_position_of_click(self):
        y = _c.mouse_pos[1] - self.rect.y - self._text_y - self._text_element.style.font.cursor_offset[1]
        line_index = int(y) // (self._text_element.style.font.line_height + self._text_element.style.font.line_spacing)

        line_index = min(max(0, line_index), len(self._text_element.lines) - 1)
        line = self._text_element.get_line(line_index)
        if line is None:
            return None
        x = _c.mouse_pos[0] - self.rect.x - self.style.padding - line.start_x

        for n in range(len(line.content)):
            if self._text_element.style.font.get_width_of(line.content[:n]) > x:
                return line.start_index + n, line_index

        return line.start_index + len(line.content), line_index

    def _set_cursor_to_end(self):
        self._cursor_index = len(self._text_element.text)
        self._update_cursor_pos()
        self._cursor_timer = 0
        self._highlighting = False
        self._highlighted = False

    def _update_cursor_pos(self, line_index=None, reset_timer=True, mode: Literal["cursor", "highlight"] = "cursor"):
        if self._text:
            index = self._cursor_index if mode == "cursor" else self._highlight_index
            if line_index is None:
                line_index = self._text_element.get_line_index_from_letter_index(index)
            line = self._text_element.get_line(line_index)

            x = line.start_x + \
                self._text_element.style.font.get_width_of(line.content[:index - line.start_index])
            if mode == "cursor":
                self._cursor_x = x
                self._cursor_line = line_index
                if reset_timer:
                    self._cursor_timer = 0
            else:
                self._highlight_x = x
                self._highlight_line = line_index

    def _remove_highlighted_area(self):
        new_text = self._text[:self._cursor_index] + self._text[self._highlight_index:]

        if self._highlighted:
            self._highlighted = False
            self._update_text(new_text)
            return True
        return False

    def _backspace(self):
        if not self._remove_highlighted_area() and self._cursor_index != 0:
            self._cursor_index -= 1

        self._update_text(self._text[:self._cursor_index] + self._text[self._cursor_index + 1:])
        self._update_cursor_pos()

    def _up_down_line(self, direction: int):
        if self._cursor_line != (len(self._text_element.lines) - 1 if direction == 1 else 0):
            line = self._text_element.get_line(self._cursor_line + direction)
            target = self._cursor_x
            output = len(line)
            for i in range(len(line)):
                w = line.start_x + self._text_element.style.font.get_width_of(line.content[:i])
                if w >= target:
                    if i == 0:
                        output = 0
                    else:
                        w2 = line.start_x + self._text_element.style.font.get_width_of(line.content[:i - 1])
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

    def event(self, event: pygame.event.Event, root: "View"):
        if self._disabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.is_active:
                self._highlighting = True
                if (result := self._get_position_of_click()) is not None:
                    self._cursor_index = result[0]
                    self._update_cursor_pos(line_index=result[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered:
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
                    self._set_cursor_to_end()

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
                self._repeated_key_timer = self.style.backspace_start_delay
                return

            if event.key == pygame.K_ESCAPE:
                self._deselect(root)

            elif event.key == pygame.K_RETURN:
                if self.multiline:
                    pass
                else:
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

            elif event.unicode not in EXCLUDED_CHARS and \
                    (self.allowed_characters is None or event.unicode in self.allowed_characters):
                if self.max_length is not None:
                    if len(self._text) >= self.max_length:
                        return
                self._remove_highlighted_area()

                self._cursor_index += 1
                self._update_text(self._text[:self._cursor_index - 1] + event.unicode +
                                  self._text[self._cursor_index - 1:])

                self._update_cursor_pos()

        elif event.type == pygame.JOYBUTTONUP and event.button == 0 and root.element_focused is self:
            self.is_active = not self.is_active

    def focus(self, root: "View", previous: Element = None, key: str = 'select'):
        if key == 'select':
            if type(root.element_focused) is TextField:
                if root.element_focused.is_active:
                    self.is_active = True
                    root.element_focused.is_active = False
                    self._set_cursor_to_end()
            return self
        else:
            return self.parent.focus(root, self, key=key)

    def _get_text(self):
        return self._text

    def set_text(self, text: str):
        self._update_text(text)

    def _set_disabled(self, value: bool):
        self._disabled = value
        self.selectable = not value
        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()
        if self._disabled:
            if self.root:
                self._deselect(self.root)

    def _get_disabled(self):
        return self.disabled

    def _get_line_height(self):
        return self._text_element.style.font.line_height + self._text_element.style.font.line_spacing

    disabled = property(
        fset=_set_disabled,
        fget=_get_disabled
    )

    _line_height = property(
        fget=_get_line_height
    )

    text = property(
        fget=_get_text,
        fset=set_text
    )
