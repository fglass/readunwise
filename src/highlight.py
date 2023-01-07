from dataclasses import dataclass
from typing import Optional

HIGHLIGHT_TOKEN = "- Your Highlight "
TRAILING_PUNCTUATION = {".", ","}


@dataclass
class Highlight:
    book: str = ""
    metadata: str = ""
    content: str = ""

    @staticmethod
    def create(clipping: str) -> Optional['Highlight']:
        if HIGHLIGHT_TOKEN not in clipping:
            return None

        try:
            parts = [part for part in clipping.split("\n") if part != ""]

            first_part = parts.pop(0)
            second_part = parts.pop(0)
            content = "\n".join(parts)

            book_title = first_part.rstrip()
            metadata = second_part.replace(HIGHLIGHT_TOKEN, "")

            return Highlight(book_title, metadata, _format_content(content))

        except IndexError:
            return None

    def is_related(self, other: 'Highlight') -> bool:
        return self.book == other.book and (self.content in other.content or other.content in self.content)


def _format_content(content: str) -> str:
    length = len(content)
    last_index = length if content[-1] not in TRAILING_PUNCTUATION else length - 1
    return content[0].upper() + content[1:last_index]
