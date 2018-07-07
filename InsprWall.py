#!/usr/bin/env python3

from configparser import ConfigParser
import os
from random import choice
from uuid import uuid4

#from bs4 import BeautifulSoup
from diskcache import Cache
from screeninfo import get_monitors
import requests

from Desktop import get_desktop_environment, set_wallpaper

NAME = "InsprWall"
VERSION = "1"

if "APPDATA" in os.environ:
    CONFIG_FILE = os.path.join(os.environ["APPDATA"], NAME)
elif "XDG_CONFIG_HOME" in os.environ:
    CONFIG_FILE = os.path.join(os.environ["XDG_CONFIG_HOME"], NAME)
else:
    CONFIG_FILE = os.path.join(os.environ["HOME"], ".config", NAME)

if "LOCALAPPDATA" in os.environ:
    CACHE_DIR = os.path.join(os.environ["LOCALAPPDATA"], NAME)
elif "XDG_CACHE_HOME" in os.environ:
    CACHE_DIR = os.path.join(os.environ["XDG_CACHE_HOME"], NAME)
else:
    CACHE_DIR = os.path.join(os.environ["HOME"], ".cache", NAME)

CONFIG_FILE = os.path.join(CONFIG_FILE, "{}.ini".format(NAME))
CONFIG = ConfigParser()
CACHE = Cache(CACHE_DIR)
CONFIG.read(CONFIG_FILE)
QUIET = CONFIG.getboolean("Other", "quiet")


def log(msg):
    if not QUIET:
        print(msg)


log("{name} version {vers}".format(name=NAME, vers=VERSION))
log("Using config: {conf}".format(conf=CONFIG_FILE))
log("Using cache: {cache}".format(cache=CACHE_DIR))


def main():
    try:
        width, height = CONFIG.getint(
            "Display", "width"), CONFIG.getint("Display", "height")
    except ValueError:
        log("Couldn't get width and height from config.")
        width = 0
        for monitor in get_monitors():
            width += monitor.width
        height = 0
        for monitor in get_monitors():
            height += monitor.height
        log("Detected width and height of {w}x{h}".format(w=width, h=height))

    # 86400 is the days --> seconds conversion factor
    cache_seconds, cache_size = CONFIG.getint(
        "Cache", "days") * 86400, CONFIG.getint("Cache", "sizem")
    # 1000000 is the megabyte --> byte conversion factor
    CACHE.reset("size_limit", cache_size * 1000000)

    reddit_prefs = {
        "sub": CONFIG.get("Reddit", "subreddit"),
        "sort": CONFIG.get("Reddit", "sort"),
        "time": CONFIG.get("Reddit", "time"),
        "nsfw": CONFIG.get("Reddit", "over18")
    }

    background = None
    try:
        # try to get image from Reddit
        req_reddit = requests.get("http://www.reddit.com/r/{sub}.json?sort={sort}&t={time}&include_over_18={nsfw}".format(
            **reddit_prefs), headers={"user-agent": "python3:{name}:{vers} (by /u/owenthewizard)".format(name=NAME, vers=VERSION)})

        # × is the unicode multiplication sign
        # don't ask
        valid_sizes = "{w}x{h} {w}X{h} {w}×{h} {w}×{h} [{h}p]".format(
            w=width, h=height).split(" ")
        if CONFIG.getboolean("Display", "2k"):
            valid_sizes.extend("[2k]", "[2K]")
        if CONFIG.getboolean("Display", "4k"):
            valid_sizes.extend("[4k]", "[4K]")
        log("Valid sizes: {sizes}".format(sizes=valid_sizes))

        for post in req_reddit.json()["data"]["children"]:
            if any(size in post["data"]["title"] for size in valid_sizes):
                log('Matched post "{title}"'.format(
                    title=post["data"]["title"]))
                url = post["data"]["url"]
                break
            else:
                log('Skipped post: "{title}"'.format(
                    title=post["data"]["title"]))

        background = requests.get(url)
        CACHE.set(uuid4(), background, expire=cache_seconds)

    except requests.exceptions.ConnectionError:
        log("No internet, using background from cache")
        background = CACHE.get(choice(list(CACHE)))

    with open(os.path.join(CACHE_DIR, "current"), mode="w+b") as out:
        out.write(background.content)
        set_wallpaper(os.path.join(CACHE_DIR, "current"),
                      get_desktop_environment())


if __name__ == "__main__":
    main()

# get quote as text
#res = requests.get("https://www.brainyquote.com/quotes_of_the_day.html")
#soup = BeautifulSoup(res.text, "lxml")
#quote = soup.find("img", {"class":"p-qotd"})
#print(quote["alt"])

# TODO
# DPI/scaling issues?
# dependency check

CACHE.close()
