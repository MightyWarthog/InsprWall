# InpsrWall

Acquire backgrounds from Reddit. Should work cross platform. In the future there will be an option to draw the [BrainyQuote](https://www.brainyquote.com) quote of the day on the background.

Background setting is done using [Desktop.py](Desktop.py) from [WeatherDesk](https://gitlab.com/bharadwaj-raju/WeatherDesk). Should also be XDG complient.

## Features

- Should be cross-platform. Report bugs!
- Scrape multiple subreddits
- Maintains an offline cache of previous backgrounds
- [UNRELEASED] draw inspirational quotes on your background (coming soon!)

## Setup

### Linux

Edit [InsprWall.ini](InsprWall.ini) as necesary and move it to a directory called `InsprWall` in your XDG config directory (usually ~/.config). Run `InsprWall.py` from the same directory as `Desktop.py`.

### Windows

TODO

### Mac

TODO

## [TODO](TODO.md)


## Help

### Error: Failed to set wallpaper. (Desktop not supported)

Export the `XDG_CURRENT_DESKTOP` or `DESKTOP_SESSION` environment variables with your apropriate desktop session. See [Desktop.py](Desktop.py) for more.

## Other

InsprWall uses components of [WeatherDesk](https://gitlab.com/bharadwaj-raju/WeatherDesk) by [Bharadwaj Raju](https://gitlab.com/bharadwaj-raju), which is licensed under the GNU General Public License v3.0.
