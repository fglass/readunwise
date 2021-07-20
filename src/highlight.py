from dataclasses import dataclass

HIGHLIGHT_TOKEN = "- Your Highlight "


@dataclass
class Highlight:
    book: str
    metadata: str
    content: str

    @staticmethod
    def create(clipping: str):
        if HIGHLIGHT_TOKEN not in clipping:
            return None

        try:
            parts = [part for part in clipping.split("\n") if part != ""]

            book_title = parts.pop(0)
            description = parts.pop(0)
            content = "\n".join(parts)

            description = description.replace(HIGHLIGHT_TOKEN, "")
            content = content.capitalize()

            return Highlight(book_title, description, content)

        except IndexError:
            return None
