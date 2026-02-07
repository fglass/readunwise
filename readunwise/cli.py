import click
import platform
from click import Context
from pathlib import Path
from readunwise.clippings import parse_clippings_file
from readunwise.highlight import Highlight
from readunwise.random_util import select_random_book, select_random_highlights
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from shutil import copyfile

DEFAULT_KINDLE_DIR = r"/Volumes/Kindle/" if platform.system() == "Darwin" else r"D:/"
DEFAULT_CLIPPINGS_FILE_PATH = Path(f"{DEFAULT_KINDLE_DIR}/documents/My Clippings.txt")
DEFAULT_OUTPUT_PATH = Path.home() / ".readunwise"

CLIPPINGS_REQUIRED_COMMANDS = {"ls", "cat", "diff", "save", "random", "discord"}

console = Console(highlight=False, soft_wrap=True)


@click.group()
@click.option(
    "--clippings_file",
    default=DEFAULT_CLIPPINGS_FILE_PATH,
    help="Clippings file from Kindle device.",
)
@click.option("--usr", is_flag=True, help="Use default file in user directory")
@click.pass_context
def cli(ctx: Context, clippings_file: str, usr: bool):
    ctx.ensure_object(dict)
    ctx.obj["clippings_file"] = DEFAULT_OUTPUT_PATH if usr else clippings_file

    if ctx.invoked_subcommand in CLIPPINGS_REQUIRED_COMMANDS:
        try:
            ctx.obj["highlights"] = parse_clippings_file(ctx.obj["clippings_file"])
        except Exception as e:
            ctx.obj["error"] = e


@cli.command(help="List clippings file.")
@click.option("-a", "--all", is_flag=True, help="List all books and their highlights")
@click.pass_context
def ls(ctx: Context, all: bool):
    table = Table()
    table.add_column("Index", justify="center"),
    table.add_column("Title")

    highlights_by_book = _get_highlights_by_book(ctx)

    for i, book in enumerate(highlights_by_book):
        table.add_row(f"[b cyan]{i + 1}", book)

        if not all:
            continue

        for j, highlight in enumerate(highlights_by_book[book]):
            table.add_row(f"[magenta]{i + 1}.{j + 1}", highlight.content)

    console.print(table)


@cli.command(help="Display highlights from a book.")
@click.argument("book")
@click.pass_context
def cat(ctx: Context, book: str):
    highlights_by_book = _get_highlights_by_book(ctx)
    book = _arg_to_book(book, highlights_by_book)

    if book not in highlights_by_book:
        console.print(f"[b red]No highlights found for {book}")
        return

    for highlight in highlights_by_book[book]:
        prefix = ">" if highlight.is_note else "-"
        console.print(f"[magenta]{prefix}[/] {highlight.content}")


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

        console.print(f"\n[b cyan]{book}")

        for highlight in highlights_by_book[book]:
            if highlight not in old_highlights:
                prefix = ">" if highlight.is_note else "-"
                console.print(f"[magenta]{prefix}[/] {highlight.content}")


@cli.command(help="Save clippings file.")
@click.argument("dst", default=DEFAULT_OUTPUT_PATH)
@click.pass_context
def save(ctx: Context, dst: str):
    src = ctx.obj["clippings_file"]
    copyfile(src, dst)
    console.print(f"Saved clippings file to [b magenta]{dst}")


@cli.command(help="Print a random highlight.")
@click.option(
    "--book", "-b", is_flag=True, help="Print all highlights from a random book."
)
@click.option("--ignore", "-i", multiple=True, help="Book title or index to ignore.")
@click.pass_context
def random(ctx: Context, book: bool, ignore: tuple[str]):
    highlights_by_book = _get_highlights_by_book(ctx)
    ignored_books = _get_ignored_books(highlights_by_book, ignore)
    random_book = select_random_book(highlights_by_book, ignored_books)

    if book:
        console.print(random_book)
        ctx.invoke(cat, book=random_book)
        return

    book_highlights = highlights_by_book[random_book]
    selected_highlight = select_random_highlights(book_highlights, n=1)[0]

    panel = Panel.fit(f"[b magenta]{selected_highlight.content}[/]\n\n- {random_book}")
    console.print(panel)


@cli.command(help="Send random highlights to a Discord channel.")
@click.argument("auth_token")
@click.argument("channel_id", type=click.INT)
@click.option("-n", default=3, help="Number of highlights to select (default: 3).")
@click.option("--ignore", "-i", multiple=True, help="Book title or index to ignore.")
@click.pass_context
def discord(
    ctx: Context, auth_token: str, channel_id: int, count: int, ignore: tuple[str]
):
    highlights_by_book = _get_highlights_by_book(ctx)
    ignored_books = _get_ignored_books(highlights_by_book, ignore)

    from discord_client import DiscordClient

    client = DiscordClient(channel_id, highlights_by_book, count, ignored_books)
    client.send(auth_token)


@cli.command(help="Display highlights from Readwise API.")
@click.argument("auth_token")
@click.option("--days", default=7, help="Number of days to look back (default: 7).")
def readwise(auth_token: str, days: int):
    try:
        from readunwise.readwise_client import ReadwiseClient

        client = ReadwiseClient(auth_token)
        highlights_by_book = client.get_highlights(days)

        if not highlights_by_book:
            console.print("[yellow]No highlights found.")
            return

        for book in highlights_by_book:
            console.print(f"\n[b cyan]{book}")

            for highlight in highlights_by_book[book]:
                prefix = ">" if highlight.is_note else "-"
                console.print(f"[magenta]{prefix}[/] {highlight.content}")
    except Exception as e:
        console.print(f"[b red]Failed to fetch highlights: {e}")


def _get_highlights_by_book(ctx: Context) -> dict[str, list[Highlight]]:
    highlights = ctx.obj.get("highlights")
    if highlights is not None:
        return highlights

    clippings_file = ctx.obj.get("clippings_file", DEFAULT_CLIPPINGS_FILE_PATH)
    error = ctx.obj.get("error")

    if error is not None:
        raise click.ClickException(
            f"Failed to load clippings file: {clippings_file}\n"
            f"Reason: {error.__class__.__name__}: {error}"
        )

    raise click.ClickException(f"No highlights loaded from: {clippings_file}")


def _get_ignored_books(highlights_by_book: dict, ignore_args: tuple[str]) -> list[str]:
    return [_arg_to_book(arg, highlights_by_book) for arg in ignore_args]


def _arg_to_book(arg: str, highlights_by_book: dict[str, list[Highlight]]) -> str:
    if arg.isnumeric():
        idx = int(arg) - 1
        return list(highlights_by_book)[idx]
    return arg


if __name__ == "__main__":
    cli()
