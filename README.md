## readunwise

Send randomly selected Kindle highlights to a Discord channel. A simple alternative to [Readwise](https://readwise.io/)

![Example Output](example-output.png)

Run as a cron job, e.g. every day at 9am:

`0 9 * * * /usr/bin/python readunwise.py <clippings_file> <discord_token> <discord_channel>`

```
usage: readunwise.py [-h] [--n N_HIGHLIGHTS] clippings_file discord_token discord_channel

Send randomly selected Kindle highlights to a Discord channel.

positional arguments:
  clippings_file    clippings text file from Kindle device (/documents/My Clippings.txt)
  discord_token     discord authentication token
  discord_channel   discord channel ID

optional arguments:
  -h, --help        show this help message and exit
  --n N_HIGHLIGHTS  number of highlights to include in message (default: 3)
```



