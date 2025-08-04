import requests
from datetime import datetime, timedelta
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
        updated_after = (datetime.now() - timedelta(days=days)).isoformat()
        highlights_by_book = {}

        url = f"{self.BASE_URL}/export/"
        params = {"updatedAfter": updated_after}

        while True:
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()

            data = response.json()

            for result in reversed(data["results"]):
                book = result["title"]

                for highlight in result["highlights"]:
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

        return highlights_by_book
