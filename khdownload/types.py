#!/usr/bin/env python3

# Imports {{{
# builtins
import contextlib
from dataclasses import dataclass, field
from functools import cached_property
import logging
import pathlib
from typing import Dict, Mapping
from urllib.parse import unquote

# 3rd party
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

# local modules
from khdownload import log as package_log
from khdownload.constants import DEFAULT_WEIGHTS
from khdownload.utils import StreamTqdm, normalize_url

# }}}


log = logging.getLogger(__name__)


@dataclass
class File(object):
    url: str
    weights: Mapping[str, int] = field(
        default_factory=lambda: DEFAULT_WEIGHTS, init=False
    )

    @property
    def name(self):
        return pathlib.Path(unquote(self.url)).name

    def download(self, folder: pathlib.Path = pathlib.Path(), hide_progress=False):
        return download(self.url, folder / self.name, hide_progress)

    def as_path(self):
        return pathlib.Path(self.url)

    @property
    def type(self):
        return self.as_path().suffix

    @property
    def weight(self):
        return self.weights[self.type]

    def __lt__(self, other):
        # reversed so that they sort by best at the front
        return self.weight > other.weight

    def __repr__(self):
        return f"<{self.__class__.__name__} {repr(self.name)}>"


@dataclass
class Song(object):
    url: str

    @cached_property
    def _raw(self):
        resp = requests.get(self.url)
        return BeautifulSoup(resp.text, "html.parser")

    @property
    def name(self):
        return pathlib.Path(unquote(self.url)).name

    @property
    def links(self):
        selector = "a .songDownloadLink"
        found = self._raw.select(selector)
        links = {normalize_url(link.parent.get("href"), self.url) for link in found}
        return links

    @cached_property
    def available(self):
        files: Dict[str, File] = {}
        for url in self.links:
            f = File(url)
            files[f.type] = f

        return files

    @property
    def files(self):
        return list(self.available.values())

    @property
    def filetypes(self):
        return list(self.available.keys())

    @property
    def best_file(self):
        ordered = sorted(self.files)
        chosen = ordered[0]
        return chosen

    @property
    def best_type(self):
        return self.best_file.type

    def download(
        self,
        folder: pathlib.Path = pathlib.Path(),
        type: str = None,
        hide_progress: bool = False,
    ):
        if type is not None:
            file = self.available[type]
        else:
            file = self.best_file

        path = file.download(folder, hide_progress=hide_progress)
        self.local = path

        return path

    def __repr__(self):
        return f"<{self.__class__.__name__} {repr(self.name)}>"


@dataclass
class Album(object):
    url: str

    @cached_property
    def _raw(self):
        resp = requests.get(self.url)
        return BeautifulSoup(resp.text, "html.parser")

    @cached_property
    def songs(self):
        return [Song(url) for url in self.song_links]

    def download(
        self, folder: pathlib.Path = None, type: str = None, hide_progress=False
    ):
        if folder is None:
            folder = pathlib.Path(self.title)

        if not folder.exists():
            folder.mkdir()

        results: Dict[pathlib.Path, Song] = {}
        with contextlib.ExitStack() as stack:
            if not hide_progress:
                stack.enter_context(logging_redirect_tqdm(loggers=[package_log]))

            log.info(f"Downloading {self.title}....")

            opts = {
                "unit": "files",
                "ncols": 90,
                "bar_format": "{l_bar}{bar}| {n_fmt}/{total_fmt} {unit}",
            }

            for song in tqdm(self.songs, disable=hide_progress, **opts):
                result = song.download(folder, type=type)
                if result is not None:
                    results[result] = song

        succeeded = list(results.keys())
        failed = [song for song in self.songs if song not in results.values()]
        return succeeded, failed

    @property
    def title(self):
        header = self._raw.select_one("#EchoTopic h2")
        return header.getText()

    @property
    def song_links(self):
        selector = "#songlist a"
        links = self._raw.select(selector)

        songs = {unquote(a.get("href")) for a in links}
        normalized = (normalize_url(url, self.url) for url in songs)

        return sorted(normalized)

    def __repr__(self):
        return f"<{self.__class__.__name__} {repr(self.title)}>"


def download(
    url: str,
    output: pathlib.Path,
    hide_progress: bool = False,
    overwrite: bool = False,
    chunk_size: int = 1024 * 4,
):
    if output.exists() and not overwrite:
        log.info(f"    {output.name} was skipped because it already exists.")
        return None

    log.info(f"Downloading {output.name}....")

    opts = {
        "unit": "B",
        "unit_scale": True,
        "unit_divisor": 1024,
        "ncols": 90,
        "bar_format": "{l_bar}{bar}| {percentage:.0f}% | {total_fmt}{unit} | {rate_fmt}",
        "leave": False,
    }

    with output.open("wb") as file:
        with requests.get(url, stream=True) as stream:
            with StreamTqdm(file, stream, disable=hide_progress, **opts) as fp:
                for chunk in stream.iter_content(chunk_size=chunk_size):
                    fp.write(chunk)

    return output
