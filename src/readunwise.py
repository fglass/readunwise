import click
from click import Context
from clippings import parse_clippings_file
from random_util import select_random_book, select_random_highlights
from typing import List, Tuple


@click.group()
@click.option("--clippings_file", default=r"D:\documents\My Clippings.txt", help="Clippings file from Kindle device.")
@click.pass_context
def cli(ctx: Context, clippings_file: str):
    ctx.ensure_object(dict)
    ctx.obj["highlights"] = parse_clippings_file(clippings_file)


@cli.command(help="List books found in the clippings file.")
@click.pass_context
def ls(ctx: Context):
    highlights_by_book = _get_highlights_by_book(ctx)
    [print(f"{i + 1}: {book}") for i, book in enumerate(highlights_by_book.keys())]


@cli.command(help="Display highlights from a book.")
@click.argument("book")
@click.pass_context
def cat(ctx: Context, book: str):
    highlights_by_book = _get_highlights_by_book(ctx)
    book = _arg_to_book(book, highlights_by_book)

    if book not in highlights_by_book:
        print(f"No highlights found for {book}")
        return

    for highlight in highlights_by_book[book]:
        print(f"- {highlight.content}")


@cli.command(help="Print a random highlight.")
@click.option("--ignore", "-i", multiple=True, help="Book title or index to ignore.")
@click.pass_context
def random(ctx: Context, ignore: Tuple[str]):
    highlights_by_book = _get_highlights_by_book(ctx)
    ignored_books = _get_ignored_books(highlights_by_book, ignore)
    random_book = select_random_book(highlights_by_book, ignored_books)

    book_highlights = highlights_by_book[random_book]
    selected_highlight = select_random_highlights(book_highlights, n=1)[0]

    print("-" * 50)
    print(f"{selected_highlight.content}\n\n- {random_book}")
    print("-" * 50)


@cli.command(help="Send random highlights to a Discord channel.")
@click.argument("auth_token")
@click.argument("channel_id", type=click.INT)
@click.option("--count", "-c", default=3, help="Number of highlights to select (default: 3).")
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
