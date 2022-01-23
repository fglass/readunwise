import logging
from discord import Client, Embed
from random_util import select_random_book, select_random_highlights

MAX_FIELD_SIZE = 1024


class DiscordClient(Client):
    def __init__(self, channel_id: int, highlights_by_book: dict, ignored_books: list, n_highlights: int):
        super().__init__()
        self._channel = None
        self._channel_id = channel_id
        self._highlights_by_book = highlights_by_book
        self._ignored_books = ignored_books
        self._n_highlights = n_highlights
        logging.info(f"Ignoring: {', '.join(ignored_books)}")

    def send(self, token: str):
        self.run(token)

    async def on_ready(self):
        self._channel = self.get_channel(self._channel_id)

        logging.info(f"Sending {self._n_highlights} highlights...")
        await self._send_message()

        logging.info("Exiting...")
        await self.close()

    async def _send_message(self):
        random_book = select_random_book(self._highlights_by_book, self._ignored_books)
        book_highlights = self._highlights_by_book[random_book]
        selected_highlights = select_random_highlights(book_highlights, self._n_highlights)

        embed = _create_embed(random_book, selected_highlights)
        await self._channel.send(embed=embed)


def _create_embed(book: str, highlights: list) -> Embed:
    embed = Embed(title=f"**📘 {book}**", color=0xfffff)
    [embed.add_field(name="━" * 10, value=_format_content(highlight.content), inline=False) for highlight in highlights]
    return embed


def _format_content(content: str) -> str:
    field = f"⭐ {content}"
    return field[:MAX_FIELD_SIZE]
