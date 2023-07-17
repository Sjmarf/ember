from typing import Optional, Sequence
from ...size import SizeType, Size, OptionalSequenceSizeType, load_size

from .element import Element


class ContentWMixin(Element):
    def __init__(self, *args, content_w: Optional[SizeType] = None, **kwargs):
        self._content_w: Optional[Size] = None
        super().__init__(*args, **kwargs)
        self.set_content_w(content_w, _update=False)

    @property
    def content_w(self) -> Optional[Size]:
        return self._content_w

    @content_w.setter
    def content_w(self, value: Optional[SizeType]) -> None:
        self.set_content_w(value)

    def set_content_w(self, value: Optional[SizeType], _update=True) -> None:
        """
        Set the content_w of the element.
        """
        self._content_w: Optional[Size] = (
            self._style.content_size[0] if value is None else load_size(value)
        )
        if _update:
            self._update_rect_chain_up()


class ContentHMixin(Element):
    def __init__(self, *args, content_h: Optional[SizeType] = None, **kwargs):
        self._content_h: Optional[Size] = None
        super().__init__(*args, **kwargs)
        self.set_content_h(content_h, _update=False)

    @property
    def content_h(self) -> Optional[Size]:
        return self._content_h

    @content_h.setter
    def content_h(self, value: Optional[SizeType]) -> None:
        self.set_content_h(value)

    def set_content_h(self, value: Optional[SizeType], _update=True) -> None:
        """
        Set the content_w of the element.
        """
        self._content_h: Optional[Size] = (
            self._style.content_size[1] if value is None else load_size(value)
        )
        if _update:
            self._update_rect_chain_up()

class ContentSizeMixin(ContentWMixin, ContentHMixin):
    def __init__(
        self,
        *args,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        **kwargs,
    ):
        if not isinstance(content_size, Sequence):
            content_size = content_size, content_size

        content_w = content_w if content_w is not None else content_size[0]
        content_h = content_h if content_h is not None else content_size[1]

        super().__init__(
            *args,
            content_w=content_w,
            content_h=content_h,
            **kwargs
        )

    @property
    def content_size(self) -> tuple[Optional[Size], Optional[Size]]:
        return self._content_w, self._content_h

    @content_size.setter
    def content_size(self, value: OptionalSequenceSizeType) -> None:
        self.set_content_size(value)

    def set_content_size(
        self, value: OptionalSequenceSizeType, _update=True
    ) -> None:
        if not isinstance(value, Sequence):
            value = value, value

        self.set_content_w(value[0], _update=_update)
        self.set_content_h(value[1], _update=_update)
