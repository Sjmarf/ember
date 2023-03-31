import pygame
import math
from typing import Union, TYPE_CHECKING

import ember.event

if TYPE_CHECKING:
    from ember.ui.view import View

from ember.size import Size

class Element:
    def __init__(self, width: Union[Size, int] = 20, height: Union[Size, int] = 20, selectable=True):
        self.root = None
        self.parent = None
        self._disabled = False

        self.animation = None
        self.visible = True
        self.selectable = selectable
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.set_size(width, height)

    def set_size(self, width: float = 20, height: float = 20):
        self.width = Size(width) if type(width) in {int, float} else width
        self.height = Size(height) if type(height) in {int, float} else height

    def set_width(self, value):
        self.width = Size(value) if type(value) in {int, float} else value

    def set_height(self, value):
        self.height = Size(value) if type(value) in {int, float} else value

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        self.rect.update(round(pos[0]),round(pos[1]),
                         round(self.get_width(max_size[0], _ignore_fill_width=_ignore_fill_width)),
                         round(self.get_height(max_size[1], _ignore_fill_height=_ignore_fill_height)))

    def update_a(self, root: "View"):
        """
        Update element, with animations.
        :param root:
        :return:
        """
        if self.animation is not None:
            self.animation.update(root)
        else:
            self.update(root)

    def update(self, root:"View"):
        pass

    def render_a(self, surface: pygame.Surface, offset: tuple[int,int], root: "View",
                 alpha: int = 255):
        """
        Render element, with animations.
        :param offset:
        :param surface:
        :param alpha:
        :param root:
        :return:
        """

        if self.animation is not None:
            self.animation.render(surface, offset, root, alpha=alpha)
            if self.animation.timer <= 0:
                self.animation = None
                new_event = pygame.event.Event(ember.event.TRANSITIONFINISHED, element=self)
                pygame.event.post(new_event)
        else:
            self.render(surface, offset, root, alpha=alpha)

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View",
               alpha: int = 255):
        pass

    def get_width(self, max_width: int, _ignore_fill_width: bool = False):
        if self.width.mode == 2:
            if _ignore_fill_width:
                return max_width
            return max_width * self.width.percentage + self.width.value
        elif self.width.mode == 1:
            if hasattr(self, "_fit_width"):
                return self._fit_width + self.width.value
            else:
                raise AttributeError(f"Element of type '{type(self).__name__}' cannot have a FIT width.")
        else:
            return self.width.value

    def get_height(self, max_height: int, _ignore_fill_height: bool = False):
        if self.height.mode == 2:
            if _ignore_fill_height:
                return max_height
            return max_height * self.height.percentage + self.height.value
        elif self.height.mode == 1:
            if hasattr(self, "_fit_height"):
                return self._fit_height + self.height.value
            else:
                raise AttributeError(f"Element of type '{type(self).__name__}' cannot have a FIT height.")
        else:
            return self.height.value

    def set_parent(self, parent):
        self.parent = parent

    def set_root(self, root):
        self.root = root

    def get_parent_tree(self):
        parents = [self.parent]
        while True:
            if not hasattr(parents[-1], "parent"):
                break            
            next_parent = parents[-1].parent
            if not hasattr(next_parent, "parent"):
                break
            parents.append(next_parent)
        return parents

    def focus(self, root: "View", previous: "Element" = None, key: str = 'select'):
        """
        Selects the element.
        """
        # 'previous' is used for going back up the chain - it is set to None when going downwards
        if key == 'select':
            return self
        else:
            # Go up a level and try again
            return self.parent.focus(root, self, key=key)

    def _get_disabled(self):
        return self._disabled

    def set_disabled(self, value: bool):
        self._disabled = value

    disabled = property(
        fget=_get_disabled,
        fset=set_disabled
    )

ElementType = Union[str, Element]