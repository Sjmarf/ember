import pygame
from typing import Union, Optional, TYPE_CHECKING, Sequence
from enum import Enum

from .. import common as _c
from ..event import TEXTFIELDCLOSED, TEXTFIELDMODIFIED
from .base.element import Element
from .text import Text
from .v_scroll import VScroll
from .h_scroll import HScroll
from .base.scroll import Scroll
from ember_ui.ui.base.mixin.style import Style
from ember_ui.ui.base.mixin.interactive import Interactive



from ..size import SizeType, FILL, FIT, OptionalSequenceSizeType
from ember_ui.position import PositionType, CENTER, SequencePositionType

from .. import log

if TYPE_CHECKING:
    from .view import ViewLayer
    from ember_ui.style.style import TextFieldStyle

# Contains sus characters
EXCLUDED_CHARS = ["", "\t", "\x00"]


class Cursor:
    def __init__(self, text_field: "TextField"):
        self.text_field = text_field
        self.x = 0
        self.letter_index = 0
        self.line_index = 0

    def update_pos(self):
        self.line_index = (
            self.text_field._text_element.get_line_index_from_letter_index(
                self.letter_index
            )
        )
        line = self.text_field._text_element.get_line(self.line_index)

        self.x = (
            line.start_x
            + self.text_field._text_element._style.font.get_width_of_line(
                line.content[: self.letter_index - line.start_index],
                variant=self.text_field._text_element._variant,
            )
            - self.text_field._text_element._style.font.character_padding[0]
        )


class HighlightState(Enum):
    NONE = 1
    HIGHLIGHTING = 2
    HIGHLIGHTED = 3


class TextField(Interactive, Style, Element):
    """
    A TextField is an interactive Element.

    Internally, the TextField uses a :py:class:`ember.ui.Text` object contained
    within a :py:class:`ember.ui.VScroll` or :py:class:`ember.ui.HScroll` object.
    """

    def __init__(
        self,
        text: Union[str, Text] = "",
        prompt: Union[str, Text, None] = None,
        multiline: bool = False,
        hide_input: bool = False,
        max_length: Optional[int] = None,
        allowed_characters: Union[str, Sequence[str], None] = None,
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        style: Optional["TextFieldStyle"] = None,
    ):
        self._style: TextFieldStyle

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

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object responsible for managing the TextField's states.
        """

        self._multiline: bool = multiline

        self._repeating_key: Optional[int] = None

        self._cursor_timer: int = 0

        self._main_cursor = Cursor(self)
        self._highlight_cursor = Cursor(self)

        self._highlight_state: HighlightState = HighlightState.NONE

        super().__init__(
            # Element
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            style=style,
            # Interactive
            disabled=disabled,
        )

        self._repeated_key_timer: float = self._style.key_repeat_start_delay

        # If a str is passed as the element, convert to a Text object.
        if self._multiline:
            if isinstance(text, Text):
                text_style = text._style
            elif self._style.text_style is not None:
                text_style = self._style.text_style
            else:
                text_style = _c.default_styles[Text]

            element_size = (FILL - text_style.font.cursor.get_width() * 2, FIT)
        else:
            element_size = (FIT, FIT)

        if isinstance(text, str):
            self._text_element: Text = Text(
                text,
                size=element_size,
                style=self._style.text_style,
                content_pos=self._style.text_align,
            )
        else:
            self._text_element: Text = text
            text.set_size(element_size)

        if isinstance(prompt, str):
            self._prompt: Text = Text(
                prompt,
                size=element_size,
                style=self._style.prompt_style,
                content_pos=self._style.text_align,
            )
        else:
            self._prompt: Text = prompt
            if prompt:
                prompt.set_size(element_size)

        if self._multiline:
            self._scroll: Scroll = VScroll(
                self._text_element,
                size=self._style.default_v_scroll_size,
                style=self._style.scroll_style,
            )
        else:
            self._scroll: Scroll = HScroll(
                self._text_element,
                size=self._style.default_h_scroll_size,
                over_scroll=[self._text_element._style.font.cursor.get_width()] * 2,
                style=self._style.scroll_style,
                content_pos=(self._text_element._content_x, CENTER),
            )

        self._scroll._set_parent(self)
        self._scroll_offset = (0, 0)
        self._update_text(self._text_element.text, send_event=False)

        if max_length is not None and len(self._text) > self.max_length:
            raise ValueError(
                f"Text length ({len(self._text)}) is greater than max_length {self.max_length}."
            )

        log.size.line_break()
        log.size.info(self, "TextField created, starting chain up...")

        with log.size.indent:
            self.update_min_size()

    def __repr__(self) -> str:
        return f"<TextField({self._text_element})>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)
        # Decide which background image to draw

        self.state_controller.set_state(
            self._style.state_func(self), transitions=(self._style.material_transition,)
        )
        self.state_controller.render(
            surface,
            (
                rect.x - surface.get_abs_offset()[0],
                rect.y - surface.get_abs_offset()[1],
            ),
            rect.size,
            alpha,
        )

        if self._text:
            # Draw highlight
            if self.is_active:
                if (
                    self._highlight_state != HighlightState.NONE
                    and self._scroll._subsurf
                ):
                    if self._highlight_state == HighlightState.HIGHLIGHTING:
                        if (result := self._get_position_of_click()) is not None:
                            self._highlight_cursor.letter_index = result[0]
                            self._highlight_cursor.update_pos()

                        if (
                            self._highlight_cursor.letter_index
                            != self._main_cursor.letter_index
                        ):
                            # If the position of the click-up is not the same as the position of the click-down,
                            # the user is trying to highlight
                            start_cursor, end_cursor = sorted(
                                (self._main_cursor, self._highlight_cursor),
                                key=lambda x: x.letter_index,
                            )

                    else:
                        start_cursor, end_cursor = (
                            self._main_cursor,
                            self._highlight_cursor,
                        )

                    if (
                        self._highlight_cursor.letter_index
                        != self._main_cursor.letter_index
                    ):
                        start_line = self._text_element.get_line(
                            start_cursor.line_index
                        )
                        end_line = self._text_element.get_line(end_cursor.line_index)

                        scroll_offset = self._scroll._subsurf.get_abs_offset()
                        scroll_offset = (
                            self._text_element._int_rect.x - scroll_offset[0],
                            self._text_element._int_rect.y - scroll_offset[1],
                        )

                        y = (
                            start_line.line_index * self._line_height
                            + self._text_element._style.font.cursor_offset[1]
                            + scroll_offset[1]
                        )

                        if start_cursor.line_index == end_cursor.line_index:
                            # One-line highlight
                            self._render_highlight(
                                start_cursor.x
                                + scroll_offset[0]
                                + self._text_element._style.font.cursor_offset[0],
                                y,
                                end_cursor.x - start_cursor.x,
                            )

                        else:
                            # Top line
                            self._render_highlight(
                                start_cursor.x
                                + scroll_offset[0]
                                + self._text_element._style.font.cursor_offset[0],
                                y,
                                start_line.width - start_cursor.x + start_line.start_x,
                            )

                            # Middle lines
                            for line_index in range(
                                start_line.line_index + 1, end_line.line_index
                            ):
                                y += self._line_height
                                line = self._text_element.get_line(line_index)
                                self._render_highlight(
                                    line.start_x
                                    + scroll_offset[0]
                                    + self._text_element._style.font.cursor_offset[0],
                                    y,
                                    line.width,
                                )

                            # Bottom line
                            y += self._line_height
                            self._render_highlight(
                                end_line.start_x
                                + scroll_offset[0]
                                + self._text_element._style.font.cursor_offset[0],
                                y,
                                end_cursor.x - end_line.start_x,
                            )

        self._scroll.render(surface, offset, alpha=alpha)

        # Draw cursor
        if self.is_active:
            if self._highlight_state == HighlightState.NONE:
                self._cursor_timer += _c.delta_time
                if self._cursor_timer < self._style.cursor_blink_speed:
                    cursor_x = (
                        self._text_element._int_rect.x
                        + self._main_cursor.x
                        - self._text_element._style.font.character_padding[0]
                        if self._text == ""
                        else self._text_element._int_rect.x
                        + self._main_cursor.x
                        + self._text_element._style.font.cursor_offset[0]
                    )

                    cursor = self._text_element._style.font.cursor.copy()
                    cursor.fill(
                        self._style.cursor_color, special_flags=pygame.BLEND_RGB_ADD
                    )
                    cursor.set_alpha(alpha)

                    cursor_y = (
                        (
                            self._prompt.rect.y
                            if (self._prompt is not None and self._text == "")
                            else self._text_element.rect.y
                        )
                        + self._text_element._style.font.cursor_offset[1]
                        + self._main_cursor.line_index * self._line_height
                        - self._scroll._subsurf.get_abs_offset()[1]
                    )

                    self._scroll._subsurf.blit(
                        cursor,
                        (
                            cursor_x - self._scroll._subsurf.get_abs_offset()[0],
                            cursor_y,
                        ),
                    )
                if self._cursor_timer > self._style.cursor_blink_speed * 2:
                    self._cursor_timer = 0

    def _render_highlight(self, x: int, y: int, w: int) -> None:
        pygame.draw.rect(
            self._scroll._subsurf,
            self._style.highlight_color,
            (
                x,
                y,
                w,
                self._text_element._style.font.cursor.get_height(),
            ),
        )

    def _update(self) -> None:
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

        if self._highlight_state == HighlightState.HIGHLIGHTING:
            if not self._scroll._scroll.playing:
                if self._multiline:
                    self._scroll.scroll_to_show_position(
                        _c.mouse_pos[1], size=self._line_height
                    )
                else:
                    self._scroll.scroll_to_show_position(
                        _c.mouse_pos[0], size=self._line_height
                    )

        self.is_hovered = self.rect.collidepoint(_c.mouse_pos)

        self._scroll._update()

        if self._prompt is not None:
            self._prompt._update()

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        super()._update_rect(surface, x, y, w, h)
    
        element_w = self._scroll.get_abs_w(w)
        element_h = self._scroll.get_abs_h(h)

        element_x = x + w / 2 - element_w / 2
        element_y = y + h / 2 - element_h / 2
        
        if not self.visible:
            self._scroll.visible = False
        elif (
            element_x + element_w < surface.get_abs_offset()[0]
            or element_x > surface.get_abs_offset()[0] + surface.get_width()
            or element_y + element_h < surface.get_abs_offset()[1]
            or element_y > surface.get_abs_offset()[1] + surface.get_height()
        ):
            self._scroll.visible = False
        else:
            self._scroll.visible = True

        with log.size.indent:
            self._scroll._update_rect(
                surface, element_x, element_y, element_w, element_h
            )

        # if self.is_active:
        #     self._update_cursor_pos(reset_timer=False, mode=Cursor.MAIN)
        #     self._update_cursor_pos(reset_timer=False, mode=Cursor.HIGHLIGHT)

    def update_ancestry(self, layer: "ViewLayer") -> None:
        log.ancestry.info(self, f"Set layer to {layer}")
        self.layer = layer
        self._scroll.update_ancestry(layer)
        if self._prompt:
            self._prompt.update_ancestry(layer)

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if direction == _c.FocusDirection.IN:
            if isinstance(self.layer.element_focused, TextField):
                if self.layer.element_focused.is_active:
                    self.is_active = True
                    self.layer.element_focused.is_active = False
                    self._set_cursor_to_end()
            return self
        else:
            return self.parent._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        if self._disabled:
            return False

        if self._scroll._event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.is_active:
                # Start highlighting
                self._highlight_state = HighlightState.HIGHLIGHTING
                if (result := self._get_position_of_click()) is not None:
                    self._main_cursor.letter_index = result[0]
                    self._main_cursor.update_pos()
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered or self._highlight_state == HighlightState.HIGHLIGHTING:
                if self.is_active:
                    # If the position of the click-up is not the same as the position of the click-down,
                    # the user is trying to highlight
                    if self._text:
                        if self._highlight_state == HighlightState.HIGHLIGHTING:
                            if (
                                self._main_cursor.letter_index
                                != self._highlight_cursor.letter_index
                            ):
                                self._highlight_state = HighlightState.HIGHLIGHTED

                                self._main_cursor, self._highlight_cursor = sorted(
                                    (self._main_cursor, self._highlight_cursor),
                                    key=lambda x: x.letter_index,
                                )
                            else:
                                self._highlight_state = HighlightState.NONE
                        self._cursor_timer = 0
                    return True
                else:
                    # If the user clicks inside the TextField, it becomes active
                    self.is_active = True
                    if self.layer.element_focused is not self and isinstance(
                        self.layer.element_focused, TextField
                    ):
                        self.layer.element_focused.is_active = False
                    self.layer._focus_element(self)
                    # Cursor is moved to mouse position
                    if (result := self._get_position_of_click()) is not None:
                        self._main_cursor.letter_index = result[0]
                        self._main_cursor.update_pos()
                    self._highlight_state = HighlightState.NONE
                    return True

            elif self.is_active:
                # When the user clicks outside the TextField, it is deactivated
                self.layer._focus_element(None)
                # False is returned because we don't want to stop the chain here
                self._highlight_state = HighlightState.NONE
                return False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN and self.layer.element_focused is self:
                if not self.is_active:
                    self.is_active = True
                    self._set_cursor_to_end()
                    return True

            elif event.key == self._repeating_key:
                self._repeating_key = None
                return False

        elif event.type == pygame.KEYDOWN and self.is_active:
            mods = pygame.key.get_mods()
            if self._run_keypress(event.key):
                # Start keypress repetition
                self._repeating_key = event.key
                self._repeated_key_timer = self._style.key_repeat_start_delay
                return True

            if event.key == pygame.K_ESCAPE:
                self.layer._focus_element(None)
                return True

            elif event.key == pygame.K_RETURN and not self._multiline:
                self.layer._focus_element(None)
                return True

            elif (
                mods & pygame.KMOD_META
                or mods & pygame.KMOD_LCTRL
                or mods & pygame.KMOD_RCTRL
            ):
                if event.key == pygame.K_a:
                    # Select all
                    self._highlight_state = HighlightState.HIGHLIGHTED
                    self._main_cursor.letter_index = 0
                    self._highlight_cursor.letter_index = (
                        len(self._text_element.text) + 1
                    )
                    self._main_cursor.update_pos()
                    self._highlight_cursor.update_pos()
                    return True

                elif event.key == pygame.K_c:
                    # copy
                    data = self._text[
                        self._main_cursor.letter_index : self._highlight_cursor.letter_index
                    ]
                    pygame.scrap.put_text(data)
                    return True

                elif event.key == pygame.K_v:
                    # paste
                    data = pygame.scrap.get_text()

                    new_text = (
                        self._text[: self._main_cursor.letter_index]
                        + data
                        + self._text[self._main_cursor.letter_index :]
                    )

                    if self.max_length is not None:
                        if len(new_text) >= self.max_length:
                            return False

                    self._remove_highlighted_area()
                    self._update_text(new_text)
                    self._main_cursor.letter_index += len(data)
                    self._main_cursor.update_pos()
                    return True

            else:
                # Add letter to text
                char = "\n" if event.unicode == "\r" else event.unicode
                if char not in EXCLUDED_CHARS and (
                    self.allowed_characters is None or char in self.allowed_characters
                ):
                    if self.max_length is not None:
                        if len(self._text) >= self.max_length:
                            return False
                    self._remove_highlighted_area()

                    self._main_cursor.letter_index += 1
                    self._update_text(
                        self._text[: self._main_cursor.letter_index - 1]
                        + char
                        + self._text[self._main_cursor.letter_index - 1 :]
                    )

                    self._main_cursor.update_pos()
                    self._scroll_to_cursor()
                    return True

        elif (
            event.type == pygame.JOYBUTTONUP
            and event.button == 0
            and self.layer.element_focused is self
        ):
            self.is_active = not self.is_active
            return True

        elif (
            event.type == pygame.JOYBUTTONDOWN
            and event.button == 1
            and self.layer.element_focused is self
        ):
            self.is_active = False
            return True

        return False

    def _on_unfocus(self) -> None:
        if self.is_active:
            self.is_active = False
            event = pygame.event.Event(TEXTFIELDCLOSED, element=self, text=self._text)
            pygame.event.post(event)

    def _update_text(self, text: str, send_event: bool = True) -> None:
        """
        Updates the text on the TextField. For internal use only.
        """
        self._text = text
        self._text_element.set_text("•" * len(text) if self.hide_input else text)
        self._cursor_timer = 0
        if send_event:
            event = pygame.event.Event(TEXTFIELDMODIFIED, element=self, text=text)
            pygame.event.post(event)
        if text != "":
            if self._scroll.element == self._prompt:
                pass
                # self._text_element._check_for_surface_update(
                #     max_width=self._prompt.get_abs_width()
                # )
            self._scroll.set_element(self._text_element)
        elif self._prompt is not None:
            self._scroll.set_element(self._prompt)

    def _get_position_of_click(self) -> tuple[int, int]:
        """
        Returns the letter index and line index of the mouse position.
        """
        y = (
            _c.mouse_pos[1]
            - self._text_element.rect.y
            - self._text_element._style.font.cursor_offset[1]
        )
        line_index = int(y) // (
            self._text_element._style.font.line_height
            + self._text_element._style.font.line_spacing
        )

        line_index = min(max(0, line_index), len(self._text_element.lines) - 1)
        line = self._text_element.get_line(line_index)
        if line is None:
            return None
        target_x = _c.mouse_pos[0] - self._text_element.rect.x - line.start_x

        prev_x = 0

        if target_x <= self._text_element._style.font.character_padding[0]:
            return line.start_index, line_index

        target_x += self._text_element._style.font.character_padding[0]

        for n in range(len(line.content)):
            if (
                current_x := self._text_element._style.font.get_width_of_line(
                    line.content[:n], variant=self._text_element._variant
                )
            ) > target_x:
                result = line.start_index + n
                if abs(target_x - prev_x) < abs(target_x - current_x):
                    result -= 1
                return result, line_index
            prev_x = current_x

        return line.start_index + len(line.content), line_index

    def _set_cursor_to_end(self) -> None:
        self._main_cursor.letter_index = len(self._text_element.text)
        self._main_cursor.update_pos()
        self._cursor_timer = 0
        self._highlight_state = HighlightState.NONE

    def _scroll_to_cursor(self):
        if not self._scroll._scroll.playing:
            self._scroll._scrollbar_calc()
            if self._multiline:
                self._scroll.scroll_to_show_position(
                    self._text_element.rect.y
                    + self._main_cursor.line_index * self._line_height,
                    size=self._line_height,
                    duration=0,
                )
            else:
                self._scroll.scroll_to_show_position(
                    self._text_element.rect.x + self._main_cursor.x,
                    size=self._text_element._style.font.cursor.get_width(),
                    offset=3,
                    duration=0,
                )

    def _remove_highlighted_area(self) -> bool:
        new_text = (
            self._text[: self._main_cursor.letter_index]
            + self._text[self._highlight_cursor.letter_index :]
        )

        if self._highlight_state == HighlightState.HIGHLIGHTED:
            self._highlight_state = HighlightState.NONE
            self._update_text(new_text)
            self._main_cursor.update_pos()
            return True
        return False

    def _backspace(self) -> None:
        if not self._remove_highlighted_area() and self._main_cursor.letter_index != 0:
            self._main_cursor.letter_index -= 1

            self._update_text(
                self._text[: self._main_cursor.letter_index]
                + self._text[self._main_cursor.letter_index + 1 :]
            )
        self._main_cursor.update_pos()

    def _up_down_line(self, direction: int) -> None:
        """
        If the direction is 1, the cursor is moved down one line. If it is -1, the cursor is moved up one line.
        """
        if self._main_cursor.line_index != (
            len(self._text_element.lines) - 1 if direction == 1 else 0
        ):
            line = self._text_element.get_line(self._main_cursor.line_index + direction)
            target = self._main_cursor.x
            output = len(line)
            for i in range(len(line)):
                w = line.start_x + self._text_element._style.font.get_width_of_line(
                    line.content[:i], variant=self._text_element._variant
                )
                if w >= target:
                    if i == 0:
                        output = 0
                    else:
                        w2 = (
                            line.start_x
                            + self._text_element._style.font.get_width_of_line(
                                line.content[: i - 1],
                                variant=self._text_element._variant,
                            )
                        )
                        if abs(w2 - target) < abs(w - target):
                            output = i - 1
                        else:
                            output = i

                    break

            self._main_cursor.letter_index = line.start_index + output
            self._main_cursor.update_pos()
            self._cursor_timer = 0
            self._scroll_to_cursor()

    def _run_keypress(self, key: int) -> bool:
        """
        Manages keypresses that can be repeated. Returns True if a keypress was executed.
        """
        if self._highlight_state == HighlightState.NONE and key in {
            pygame.K_LEFT,
            pygame.K_RIGHT,
        }:
            if key == pygame.K_LEFT and self._main_cursor.letter_index != 0:
                self._main_cursor.letter_index -= 1

            if key == pygame.K_RIGHT and self._main_cursor.letter_index != len(
                self._text_element.text
            ):
                self._main_cursor.letter_index += 1

            self._main_cursor.update_pos()
            self._cursor_timer = 0
            self._scroll_to_cursor()
            return True

        elif key == pygame.K_DOWN:
            if self.multiline:
                self._up_down_line(1)
                return True

        elif key == pygame.K_UP:
            if self.multiline:
                self._up_down_line(-1)
                return True

        elif key == pygame.K_BACKSPACE:
            self._backspace()
            return True

        elif key == pygame.K_DELETE:
            # Delete ahead of the cursor
            if (
                not self._remove_highlighted_area()
                and self._main_cursor.letter_index != len(self._text)
            ):
                self._update_text(
                    self._text[: self._main_cursor.letter_index]
                    + self._text[self._main_cursor.letter_index + 1 :]
                )
                self._main_cursor.update_pos()
                return True

    @property
    def _line_height(self) -> int:
        return self._get_line_height()

    def _get_line_height(self) -> int:
        return (
            self._text_element._style.font.line_height
            + self._text_element._style.font.line_spacing
        )

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self.set_text(text)

    def set_text(self, text: str) -> None:
        """
        Set the text on the button.
        """
        self._update_text(text)
        self._main_cursor.update_pos()

    def _set_disabled(self, value: bool) -> None:
        if self._disabled:
            if self.layer:
                self.layer._focus_element(None)
            if self.is_active:
                self.is_active = False

    def set_active(self, state: bool) -> None:
        self.is_active = state

    @property
    def multiline(self) -> bool:
        return self._multiline

    @multiline.setter
    def multiline(self, value: bool) -> None:
        self.set_multiline(value)

    def set_multiline(self, value: Optional[bool] = None) -> None:
        """
        If set to :code:`True`, text will wrap onto a second line when it reaches the end of the TextField.
        """
        if value is None:
            value = not self._multiline
        self._multiline = value

        if value:
            self._text_element.set_size(
                FILL - FILL - self._text_element._style.font.cursor.get_width() * 2, FIT
            )
            self._scroll = VScroll(
                self._text_element,
                size=self._style.default_v_scroll_size,
                style=self._style.scroll_style,
            )
        else:
            self._text_element.set_size(FIT, FIT)
            self._scroll = HScroll(
                self._text_element,
                size=self._style.default_h_scroll_size,
                style=self._style.scroll_style,
                over_scroll=[self._text_element._style.font.cursor.get_width()] * 2,
                content_pos=(self._text_element.align[0], CENTER),
            )

        self._scroll._set_parent(self)
        log.ancestry.line_break()
        log.ancestry.info(self, "TextField multiline modified - starting chain...")
        with log.ancestry.indent:
            self._scroll.update_ancestry(self.layer)

        self._update_text(self._text, send_event=False)
        log.size.line_break()
        log.mls.line_break()
        log.size.info(
            self, "TextField multiline was changed, generating Text surfaces..."
        )
        log.mls.info(
            self, "TextField multiline was changed, generating Text surfaces..."
        )
        with log.mls.indent, log.size.indent:
            self._scroll[0]._update_surface()
        self._main_cursor.update_pos()
