import click
import platform
from click import Context
from pathlib import Path
from readunwise.clippings import parse_clippings_file
from readunwise.random_util import select_random_book, select_random_highlights
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from shutil import copyfile
from typing import List, Tuple

DEFAULT_KINDLE_DIR = r"/Volumes/Kindle/" if platform.system() == "Darwin" else r"D:/"
DEFAULT_CLIPPINGS_FILE_PATH = Path(f"{DEFAULT_KINDLE_DIR}/documents/My Clippings.txt")
DEFAULT_OUTPUT_PATH = Path.home() / ".readunwise"


@click.group()
@click.option("--clippings_file", default=DEFAULT_CLIPPINGS_FILE_PATH, help="Clippings file from Kindle device.")
@click.pass_context
def cli(ctx: Context, clippings_file: str):
    ctx.ensure_object(dict)
    ctx.obj["clippings_file"] = clippings_file
    ctx.obj["highlights"] = parse_clippings_file(clippings_file)


@cli.command(help="List books found in the clippings file.")
@click.pass_context
def ls(ctx: Context):
    table = Table()
    table.add_column("Index", justify="center", style="magenta")
    table.add_column("Book Title")

    highlights_by_book = _get_highlights_by_book(ctx)

    for i, book in enumerate(highlights_by_book):
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


@cli.command(help="Compare clippings files.")
@click.argument("old_clippings_file", default=DEFAULT_OUTPUT_PATH)
@click.pass_context
def diff(ctx: Context, old_clippings_file: str):
    highlights_by_book = _get_highlights_by_book(ctx)
    old_highlights_by_book = parse_clippings_file(old_clippings_file)

    for book in highlights_by_book:
        new_highlights = highlights_by_book[book]
        old_highlights = set(old_highlights_by_book.get(book, []))

        if len(new_highlights) <= len(old_highlights):
            continue

        rprint(f"\n[b cyan]{book}")

        for highlight in highlights_by_book[book]:
            if highlight not in old_highlights:
                rprint(f"[magenta]-[/] {highlight.content}")


@cli.command(help="Copy clippings file.")
@click.argument("dst", default=DEFAULT_OUTPUT_PATH)
@click.pass_context
def cp(ctx: Context, dst: str):
    copyfile(src=ctx.obj["clippings_file"], dst=dst)
    rprint(f"Copied clippings file to [b magenta]{dst}")


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
    highlights_by_book = _get_highlights_by_book(ctx)
    ignored_books = _get_ignored_books(highlights_by_book, ignore)

    from discord_client import DiscordClient
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
