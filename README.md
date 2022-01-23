# readunwise

A simple CLI alternative to [Readwise](https://readwise.io/)
```
usage: readunwise.py [-h] clippings_file {list,export,random,send} ...
```

## List

List books found in the clippings file

## Export

Export a book's highlights as markdown. This can then be imported into Notion and other note-taking apps

## Random

Print a random highlight to stdout

## Send

Send random highlights to a Discord channel. This can be run as a cron job e.g. every day at 9am:

`0 9 * * * python3 home/pi/readunwise/src/readunwise.py <file> send <args>`

![Example Message](example-message.png)