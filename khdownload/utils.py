#!/usr/bin/env python3

# Imports {{{
# builtins
import pathlib
from typing import Collection, Mapping
from urllib.parse import urlparse, unquote

# 3rd party
import requests
from bs4 import BeautifulSoup

# local modules
from khdownload.constants import DEFAULT_WEIGHTS

# }}}


def normalize_url(url, parent):
    """
    Convert a relative URL to an absolute one.

    Converts the URL by looking at an existing, related URL.
    """
    parsed = urlparse(url)

    if not parsed.netloc:
        domain = urlparse(parent)
        return parsed._replace(scheme=domain.scheme, netloc=domain.netloc).geturl()

    return url


def scrape_album(album_url: str):
    def get_album_title(page: BeautifulSoup):
        header = page.select_one("#EchoTopic h2")
        return header.getText()

    def get_songlist(page: BeautifulSoup):
        selector = "#songlist a"
        links = page.select(selector)

        songs = {unquote(a.get("href")) for a in links}
        normalized = (normalize_url(url, album_url) for url in songs)

        return sorted(normalized)

    resp = requests.get(album_url)
    scraped = BeautifulSoup(resp.text, "html.parser")

    title = get_album_title(scraped)
    songs = get_songlist(scraped)

    return (title, songs)


def get_files_from_song_page(page: str):
    resp = requests.get(page)
    scraped = BeautifulSoup(resp.text, "html.parser")

    selector = "a .songDownloadLink"
    links = scraped.select(selector)
    files = {link.parent.get("href") for link in links}

    return files


def get_best_file(files: Collection[str], weights: Mapping[str, int] = DEFAULT_WEIGHTS):
    def lookup_weight(file: str):
        return weights[pathlib.Path(file).suffix]

    ordered = reversed(sorted(files, key=lookup_weight))
    chosen = next(ordered)
    return chosen
