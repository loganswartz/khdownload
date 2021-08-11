#!/usr/bin/env python3

# Imports {{{
# builtins
import pathlib
from urllib.parse import unquote

# 3rd party
import requests
from tqdm import tqdm

# local modules
from khdownload.utils import (
    get_files_from_song_page,
    normalize_url,
    scrape_album,
    get_best_file,
)

# }}}


def download_album(
    album_url,
    folder: pathlib.Path = pathlib.Path("."),
    allow_existing=True,
    hide_progress=False,
):
    album_title, songs = scrape_album(album_url)
    print(f"Downloading {album_title}....")
    if not songs:
        print(f"No songs found for {album_title}!")
        return None

    folder = folder / album_title

    try:
        folder.mkdir()
    except FileExistsError:
        print(f'"{folder.name}" already exists. Skipping...')
        if not allow_existing:
            return None

    for song_url in tqdm(
        songs,
        unit="files",
        ncols=90,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {unit}",
        disable=hide_progress,
    ):
        # get the raw list of available files for download
        files = get_files_from_song_page(normalize_url(song_url, album_url))
        files = [normalize_url(url, album_url) for url in files]

        # choose which filetype to download
        try:
            # sort filelist by suffix rankings, and take the first item
            file = get_best_file(files)
        except StopIteration:
            tqdm.write(f"    Error: no files found on {song_url}.")
            continue

        download_song(file, folder)


def download_song(
    url: str,
    folder: pathlib.Path,
    filename: str = None,
    overwrite=False,
    hide_progress=False,
):
    if filename is None:
        # extract filename from url
        filename = pathlib.Path(unquote(url)).name

    local_file = folder / filename

    if local_file.exists() and not overwrite:
        tqdm.write(f"    {filename} was skipped because it already exists.")
        return None

    tqdm.write(f"    Downloading {filename}...")

    # likely more efficient method of saving the files, albeit without a progress bar
    # with requests.get(file, stream=True) as data:
    #     with pathlib.Path(local_file).open('wb') as f:
    #         shutil.copyfileobj(data.raw, f)

    with pathlib.Path(local_file).open("wb") as f:
        with requests.get(url, stream=True) as stream:
            content_size = stream.headers.get("Content-Length")
            file_size = int(content_size) if content_size else None  # in bytes
            pbar_options = {
                "total": file_size,
                "unit": "B",
                "unit_scale": True,
                "unit_divisor": 1024,
                "ncols": 90,
                "bar_format": "{l_bar}{bar}| {percentage:.0f}% | {total_fmt}{unit} | {rate_fmt}",
                "leave": False,
                "disable": hide_progress,
            }
            with tqdm(**pbar_options) as pbar:
                for chunk in stream.iter_content(
                    chunk_size=1024 * 8
                ):  # chunk_size=None means whatever size they come in as
                    f.write(chunk)
                    pbar.update(len(chunk))
