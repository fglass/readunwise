import argparse
import logging
from highlight import Highlight
from src.discord_client import DiscordClient

CLIPPING_DELIMITER = "=========="


def _run():
    args = parser.parse_args()
    logging.info(f"Config: {vars(args)}")

    highlights_by_book = _load_highlights(args.clippings_file)

    if args.list:
        _list_books(highlights_by_book)
    elif args.send:
        client = DiscordClient(args.discord_channel, highlights_by_book, args.ignored_books, args.n_highlights)
        client.send(args.discord_token)
    else:
        logging.error("Missing action: --list, --send")


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

    logging.info(f"Found {loaded} highlights across {len(highlights)} books")

    return highlights


def _list_books(highlights_by_book: dict):
    [logging.info(f"({i + 1}) {book}") for i, book in enumerate(highlights_by_book)]


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.INFO)
    logging.getLogger("discord").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(description="Send randomly selected Kindle highlights to a Discord channel.")
    parser.add_argument("clippings_file", help="clippings file from Kindle device (/documents/My Clippings.txt)")
    parser.add_argument("-l", "--list", action="store_true", help="list discovered books")
    parser.add_argument("-s", "--send", action="store_true", help="send randomly selected highlights to a Discord channel")
    parser.add_argument("-t", dest="discord_token", help="discord bot authentication token")
    parser.add_argument("-c", dest="discord_channel", type=int,  help="discord channel ID")
    parser.add_argument("-n", type=int, default=3, dest="n_highlights", help="number of highlights to select (default: %(default)s)")
    parser.add_argument("-i", nargs='+', dest="ignored_books", help="titles of books to ignore")

    _run()
