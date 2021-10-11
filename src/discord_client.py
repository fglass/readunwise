import logging
import random
from discord import Client, Embed

MAX_FIELD_SIZE = 1024


class DiscordClient(Client):
    def __init__(self, channel_id: int, highlights_by_book: dict, ignored_books: list, n_highlights: int):
        super().__init__()
        self._channel = None
        self._channel_id = channel_id
        self._highlights_by_book = highlights_by_book
        self._ignored_books = ignored_books
        self._n_highlights = n_highlights

    def send(self, token: str):
        self.run(token)

    async def on_ready(self):
        self._channel = self.get_channel(self._channel_id)

        logging.info("Sending message...")
        await self._send_message()

        logging.info("Exiting...")
        await self.close()

    async def _send_message(self):
        random_book = self._get_random_book()
        selected_highlights = self._select_highlights(random_book)
        embed = _create_embed(random_book, selected_highlights)
        await self._channel.send(embed=embed)

    def _get_random_book(self) -> str:
        ignored_books = self._ignored_books or []
        books = [book for book in self._highlights_by_book.keys() if book not in ignored_books]
        return random.choice(books)

    def _select_highlights(self, book: str) -> list:
        book_highlights = self._highlights_by_book[book]
        n_highlights = min(len(book_highlights), self._n_highlights)
        return random.sample(book_highlights, k=n_highlights)


def _create_embed(book: str, highlights: list) -> Embed:
    embed = Embed(title=f"**📘 {book}**", color=0xfffff)
    [embed.add_field(name="━" * 10, value=_format_content(highlight.content), inline=False) for highlight in highlights]
    return embed


def _format_content(content: str) -> str:
    field = f"⭐ {content}"
    return field[:MAX_FIELD_SIZE]
