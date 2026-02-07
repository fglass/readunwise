import requests
from datetime import datetime, timedelta, timezone
from readunwise.highlight import Highlight


class ReadwiseClient:
    BASE_URL = "https://readwise.io/api/v2"

    def __init__(self, auth_token: str):
        self._auth_token = auth_token
        self._headers = {
            "Authorization": f"Token {self._auth_token}",
            "Content-Type": "application/json",
        }

    def get_highlights(self, days: int = 7) -> dict[str, list[Highlight]]:
        highlights_by_book = {}
        first_highlighted_by_book = {}

        url = f"{self.BASE_URL}/export/"
        updated_after = (datetime.now() - timedelta(days=days)).isoformat()
        params = {"updatedAfter": updated_after}

        while True:
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()

            data = response.json()

            for result in reversed(data["results"]):
                book = result["title"]

                for highlight in result["highlights"]:
                    highlighted_at = _parse_iso_datetime(
                        highlight.get("highlighted_at")
                    )

                    if highlighted_at is not None:
                        max_datetime = datetime.max.replace(tzinfo=timezone.utc)
                        first_highlighted_by_book[book] = min(
                            first_highlighted_by_book.get(book, max_datetime),
                            highlighted_at,
                        )

                    content = highlight["text"]
                    note = highlight.get("note", "")

                    if note:
                        content = f"{note} ({content})"

                    highlight = Highlight(
                        book=book,
                        metadata="",
                        content=content,
                        is_note=note != "",
                    )

                    if book not in highlights_by_book:
                        highlights_by_book[book] = []

                    highlights_by_book[book].append(highlight)

            cursor = data.get("nextPageCursor")

            if cursor is None:
                break

            params |= {"pageCursor": cursor}

        return _sort_books_by_first_highlighted(
            highlights_by_book, first_highlighted_by_book
        )


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def _sort_books_by_first_highlighted(
    highlights_by_book: dict[str, list[Highlight]],
    first_highlighted_by_book: dict[str, datetime],
) -> dict[str, list[Highlight]]:
    max_datetime = datetime.max.replace(tzinfo=timezone.utc)
    sorted_books = sorted(
        highlights_by_book,
        key=lambda book: first_highlighted_by_book.get(book, max_datetime),
    )
    return {book: highlights_by_book[book] for book in sorted_books}
