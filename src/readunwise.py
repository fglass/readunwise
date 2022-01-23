import argparse
from highlight import Highlight
from random_util import select_random_book, select_random_highlights

CLIPPING_DELIMITER = "=========="
LIST_ACTION = "list"
EXPORT_ACTION = "export"
RANDOM_ACTION = "random"
SEND_ACTION = "send"


def _execute():
    if args.action == LIST_ACTION:
        _list_books()
    elif args.action == EXPORT_ACTION:
        _export_book()
    elif args.action == RANDOM_ACTION:
        _print_random_highlight()
    elif args.action == SEND_ACTION:
        _send_highlights_to_discord()


def _load_highlights(clippings_file: str) -> dict:
    highlights = {}
    loaded = 0

    with open(clippings_file, "r+", encoding="utf8") as f:
        clippings = f.read().split(CLIPPING_DELIMITER)

    for clipping in clippings:
        highlight = Highlight.create(clipping)
        if highlight is not None:
            highlights.setdefault(highlight.book, []).append(highlight)
            loaded += 1

    return highlights


def _list_books():
    [print(f"{i + 1}: {book}") for i, book in enumerate(highlights_by_book.keys())]


def _export_book():
    book = _arg_to_book(args.book)

    if book not in highlights_by_book:
        print(f"No highlights found for {book}")
        return

    sanitised_title = book.replace(":", "")
    filename = f"{args.export_dir}/{sanitised_title}.md"

    with open(filename, "w+", encoding="utf8") as f:
        highlights = highlights_by_book[book]
        lines = [f"- {h.content}\n" for h in highlights]
        f.writelines(lines)

    print(f"Exported {filename}")


def _print_random_highlight():
    ignored_books = _get_ignored_books()
    random_book = select_random_book(highlights_by_book, ignored_books)

    book_highlights = highlights_by_book[random_book]
    selected_highlight = select_random_highlights(book_highlights, n=1)[0]

    print(f"\"{selected_highlight.content}\"\n- {random_book}")


def _send_highlights_to_discord():
    from discord_client import DiscordClient
    ignored_books = _get_ignored_books()
    client = DiscordClient(args.discord_channel, highlights_by_book, ignored_books, args.n_highlights)
    client.send(args.discord_token)


def _get_ignored_books() -> list:
    return [_arg_to_book(arg) for arg in args.ignored_books or []]


def _arg_to_book(arg: str):
    if arg.isnumeric():
        idx = int(arg) - 1
        return list(highlights_by_book)[idx]
    return arg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple alternative to Readwise.")
    parser.add_argument("clippings_file", help="clippings file from Kindle device (/documents/My Clippings.txt)")

    subparsers = parser.add_subparsers(dest="action")
    list_parser = subparsers.add_parser(LIST_ACTION, help="list books")

    export_parser = subparsers.add_parser(EXPORT_ACTION, help="export a book's highlights as markdown")
    export_parser.add_argument("book", help="book title or index")
    export_parser.add_argument("export_dir", help="export directory")

    random_parser = subparsers.add_parser(RANDOM_ACTION, help="print a random highlight")
    random_parser.add_argument("-i", nargs='+', dest="ignored_books", help="book titles or indices to ignore")

    send_parser = subparsers.add_parser(SEND_ACTION, help="send random highlights to a Discord channel")
    send_parser.add_argument("discord_token", help="discord bot authentication token")
    send_parser.add_argument("discord_channel", type=int,  help="discord channel ID")
    send_parser.add_argument("-i", nargs='+', dest="ignored_books", help="book titles or indices to ignore")
    send_parser.add_argument("-n", type=int, default=3, dest="n_highlights", help="number of highlights to select (default: %(default)s)")

    args = parser.parse_args()

    if args.action is not None:
        highlights_by_book = _load_highlights(args.clippings_file)
        _execute()
    else:
        print("Invalid arguments, see --help")
