import click
import platform
from click import Context
from clippings import parse_clippings_file
from random_util import select_random_book, select_random_highlights
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from typing import List, Tuple

DEFAULT_KINDLE_PATH = r"/Volumes/Kindle/" if platform.system() == "Darwin" else r"D:\\"
DEFAULT_CLIPPINGS_FILE = rf"{DEFAULT_KINDLE_PATH}/documents/My Clippings.txt"


@click.group()
@click.option("--clippings_file", default=DEFAULT_CLIPPINGS_FILE, help="Clippings file from Kindle device.")
@click.pass_context
def cli(ctx: Context, clippings_file: str):
    ctx.ensure_object(dict)
    ctx.obj["highlights"] = parse_clippings_file(clippings_file)


@cli.command(help="List books found in the clippings file.")
@click.pass_context
def ls(ctx: Context):
    table = Table()
    table.add_column("Index", justify="center", style="magenta")
    table.add_column("Book Title")

    highlights_by_book = _get_highlights_by_book(ctx)

    for i, book in enumerate(highlights_by_book.keys()):
        table.add_row(str(i + 1), book)

    rprint(table)


@cli.command(help="Display highlights from a book.")
@click.argument("book")
@click.pass_context
def cat(ctx: Context, book: str):
    highlights_by_book = _get_highlights_by_book(ctx)
    book = _arg_to_book(book, highlights_by_book)

    if book not in highlights_by_book:
        rprint(f"[b red]No highlights found for {book}")
        return

    for highlight in highlights_by_book[book]:
        rprint(f"[magenta]-[/] {highlight.content}")


@cli.command(help="Print a random highlight.")
@click.option("--ignore", "-i", multiple=True, help="Book title or index to ignore.")
@click.pass_context
def random(ctx: Context, ignore: Tuple[str]):
    highlights_by_book = _get_highlights_by_book(ctx)
    ignored_books = _get_ignored_books(highlights_by_book, ignore)
    random_book = select_random_book(highlights_by_book, ignored_books)

    book_highlights = highlights_by_book[random_book]
    selected_highlight = select_random_highlights(book_highlights, n=1)[0]

    panel = Panel.fit(f"[b magenta]{selected_highlight.content}[/]\n\n- {random_book}")
    rprint(panel)


@cli.command(help="Send random highlights to a Discord channel.")
@click.argument("auth_token")
@click.argument("channel_id", type=click.INT)
@click.option("-n", default=3, help="Number of highlights to select (default: 3).")
@click.option("--ignore", "-i", multiple=True, help="Book title or index to ignore.")
@click.pass_context
def discord(ctx: Context, auth_token: str, channel_id: int, count: int, ignore: Tuple[str]):
    from discord_client import DiscordClient
    highlights_by_book = _get_highlights_by_book(ctx)
    ignored_books = _get_ignored_books(highlights_by_book, ignore)
    client = DiscordClient(channel_id, highlights_by_book, count, ignored_books)
    client.send(auth_token)


def _get_highlights_by_book(ctx: Context) -> dict:
    return ctx.obj["highlights"]


def _get_ignored_books(highlights_by_book: dict, ignore_args: Tuple[str]) -> List[str]:
    return [_arg_to_book(arg, highlights_by_book) for arg in ignore_args]


def _arg_to_book(arg: str, highlights_by_book: dict) -> str:
    if arg.isnumeric():
        idx = int(arg) - 1
        return list(highlights_by_book)[idx]
    return arg


if __name__ == "__main__":
    cli()
