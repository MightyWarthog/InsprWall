#!/usr/bin/env python3

from configparser import ConfigParser
import os
from random import choice
from tempfile import NamedTemporaryFile
from uuid import uuid4

from bs4 import BeautifulSoup
from diskcache import Cache
from screeninfo import get_monitors
import requests

from Desktop import get_desktop_environment, set_wallpaper

NAME = "InsprWall"
VERSION = "DEV-UNRELEASED"

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

def main():
    CONFIG.read(CONFIG_FILE)

    try:
        width, height = CONFIG.getint("Display", "width"), CONFIG.getint("Display", "height")
    except ValueError:
        width = 0
        for monitor in get_monitors():
            width += monitor.width
        height = 0
        for monitor in get_monitors():
            height += monitor.height
    
    cache_seconds, cache_size = CONFIG.getint("Cache", "days"), CONFIG.getint("Cache", "sizem")
    CACHE.reset("cull_limit", cache_seconds)
    # 86400 is the days --> seconds conversion factor
    cache_seconds *= 86400
    # 1000000 is the megabyte --> byte conversion factor
    CACHE.reset("size_limit", cache_size * 1000000)

    reddit_prefs = {
            "sub":CONFIG["Reddit"].get("subreddit"),
            "sort":CONFIG["Reddit"].get("sort"),
            "time":CONFIG["Reddit"].get("time"),
            "nsfw":CONFIG["Reddit"].get("over18")
            }

    background = None
    try:
        # try to get image from Reddit
        req_reddit = requests.get("http://www.reddit.com/r/{sub}.json?sort={sort}&t={time}&include_over_18={nsfw}".format(**reddit_prefs), headers={"user-agent":"python3:{}:{} (by /u/owenthewizard)".format(NAME, VERSION)})
        valid_sizes = "[{w}x{h}] [{w}X{h}] [{h}p]".format(w=width, h=height).split(" ")
        if CONFIG.getbool("Display", "2k"):
            valid_sizes.extend("2k", "2K")
        if CONFIG.getbool("Display", "4k"):
            valid_size.extend("4k", "4K")
        valid_size = set(valid_size)
        for post in req_reddit.json()["data"]["children"]:
            if not valid_sizepost.isdisjoint(post["data"]["title"]):
                url = post["data"]["url"]
                break
        background = requests.get(url)
        CACHE.set(uuid4(), background, expire=cache_seconds)
    except:
        # No internet or some such
        background = CACHE.get(choice(list(CACHE)))

    with open(os.path.join(CACHE_DIR, "current"), mode="w+b") as out:
        out.write(background.content)
        set_wallpaper(os.path.join(CACHE_DIR, "current"), get_desktop_environment())

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
