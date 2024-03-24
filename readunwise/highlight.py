from dataclasses import dataclass
from typing import Optional

HIGHLIGHT_TOKEN = "- Your Highlight "
NOTE_TOKEN = "- Your Note "
TRAILING_PUNCTUATION = {".", ","}


@dataclass(frozen=True)
class Highlight:
    book: str = ""
    metadata: str = ""
    content: str = ""
    is_note: bool = False

    @staticmethod
    def create(clipping: str) -> Optional["Highlight"]:
        is_highlight = HIGHLIGHT_TOKEN in clipping
        is_note = NOTE_TOKEN in clipping

        if not is_highlight and not is_note:
            return None

        try:
            parts = [part for part in clipping.split("\n") if part != ""]

            first_part = parts.pop(0)
            second_part = parts.pop(0)
            content = "\n".join(parts)

            book_title = first_part.rstrip()
            metadata = second_part.replace(HIGHLIGHT_TOKEN, "").replace(NOTE_TOKEN, "")

            return Highlight(book_title, metadata, _format_content(content), is_note)

        except IndexError:
            return None

    def is_related(self, other: "Highlight") -> bool:
        return self.book == other.book and (
            _is_content_related(self.content, other.content)
            or _is_content_related(other.content, self.content)
        )


def _format_content(content: str) -> str:
    length = len(content)
    last_index = length if content[-1] not in TRAILING_PUNCTUATION else length - 1
    return content[0].upper() + content[1:last_index]


def _is_content_related(c1: str, c2: str) -> bool:
    return c1.lower() in c2.lower()
