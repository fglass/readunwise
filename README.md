## readunwise

A simple alternative to [Readwise](https://readwise.io/)

```
usage: readunwise.py [-h] clippings_file {list,export,send} ...
```

### List

List books found in clippings file

### Export

Export book highlights as markdown. This can then be imported into Notion and other note-taking apps

### Send

Send randomly selected highlights to a Discord channel. Run as a cron job e.g. every day at 9am:

`0 9 * * * python3 home/pi/readunwise/src/readunwise.py <file> send <args>`

![Example Message](example-message.png)