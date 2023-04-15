import pygame
from .. import common as _c


class Resizable:
    def _is_hovering_resizable_edge(self):
        if 'right' in self.resizable_side:
            if self.rect.collidepoint(self.rect.x, _c.mouse_pos[1]) and \
                    self.rect.right - 2 < _c.mouse_pos[0] < self.rect.right + 2:
                return self._set_hovering_resizable_edge('right')

        if 'left' in self.resizable_side:
            if self.rect.collidepoint(self.rect.x, _c.mouse_pos[1]) and \
                    self.rect.left - 2 < _c.mouse_pos[0] < self.rect.left + 2:
                return self._set_hovering_resizable_edge('left')

        if 'top' in self.resizable_side:
            if self.rect.collidepoint(_c.mouse_pos[0], self.rect.y) and\
                    self.rect.top - 2 < _c.mouse_pos[1] < self.rect.top + 2:
                return self._set_hovering_resizable_edge('top')

        if 'bottom' in self.resizable_side:
            if self.rect.collidepoint(_c.mouse_pos[0], self.rect.y) and \
                    self.rect.bottom - 2 < _c.mouse_pos[1] < self.rect.bottom + 2:
                return self._set_hovering_resizable_edge('bottom')

        self._set_hovering_resizable_edge(None)

    def _set_hovering_resizable_edge(self, value):
        if value == self._hovering_resize_edge:
            return

        if self._hovering_resize_edge is None:
            if value in {"left", "right"}:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)

        elif value is None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self._hovering_resize_edge = value

    def _resize(self):
        if self._hovering_resize_edge == "right":
            value = max(min(_c.mouse_pos[0] - self.rect.x, self.resize_limits[1]), self.resize_limits[0])
            self.set_size(value, self.height)
        if self._hovering_resize_edge == "left":
            value = max(min(self.rect.w + self.rect.x - _c.mouse_pos[0],
                            self.resize_limits[1]), self.resize_limits[0])
            self.set_size(value, self.height)
        if self._hovering_resize_edge == "bottom":
            value = max(min(_c.mouse_pos[1] - self.rect.y, self.resize_limits[1]), self.resize_limits[0])
            self.set_size(self.width, value)
        if self._hovering_resize_edge == "top":
            value = max(min(self.rect.h + self.rect.y - _c.mouse_pos[1],
                            self.resize_limits[1]), self.resize_limits[0])
            self.set_size(self.width, value)
