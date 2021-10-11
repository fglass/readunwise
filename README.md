## readunwise

Send randomly selected Kindle highlights to a Discord channel. A simple alternative to [Readwise](https://readwise.io/)

Run as a cron job e.g. every day at 9am: `0 9 * * * python3 home/pi/readunwise/src/readunwise.py <args>`

```
usage: readunwise.py [-h] [-l] [-s] [-t DISCORD_TOKEN] [-c DISCORD_CHANNEL]
                     [-n N_HIGHLIGHTS] [-i IGNORED_BOOKS [IGNORED_BOOKS ...]]
                     clippings_file

Send randomly selected Kindle highlights to a Discord channel.

positional arguments:
  clippings_file        clippings file from Kindle device (/documents/My
                        Clippings.txt)

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list discovered books
  -s, --send            send randomly selected highlights to a Discord channel
  -t DISCORD_TOKEN      discord bot authentication token
  -c DISCORD_CHANNEL    discord channel ID
  -n N_HIGHLIGHTS       number of highlights to select (default: 3)
  -i IGNORED_BOOKS [IGNORED_BOOKS ...]
                        titles of books to ignore
```

![Example Output](example-output.png)
