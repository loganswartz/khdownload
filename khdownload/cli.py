#!/usr/bin/env python3

# Imports {{{
# builtins
import logging
import pathlib
import sys

# 3rd party
import click

# local modules
from khdownload import log
from khdownload.types import Album
from khdownload.utils import convert_files

# }}}


log.setLevel(logging.INFO)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
log.addHandler(sh)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("urls", nargs=-1)
@click.option(
    "-f",
    "--from-file",
    "list_file",
    type=click.File(),
    help="Path to a text file containing album URLs (separated by newlines)",
)
@click.option(
    "-o",
    "--output",
    help="Path specifying where the albums should be saved",
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    default=None,
)
@click.option("-t", "--type", help="Download a specific filetype")
@click.option(
    "-c", "--convert-m4a", help="Convert any .m4a files to .flac", is_flag=True
)
def cli(urls, list_file, output, type, convert_m4a):
    urls = set(urls)
    if list_file:
        urls = urls.union(
            {url.strip() for url in list_file.splitlines() if url.strip()}
        )
    if not urls:
        print("Please specify a URL.")
        sys.exit(1)

    for url in urls:
        album = Album(url)
        succeeded, failed = album.download(folder=output, type=type)
        if convert_m4a:
            results = convert_files(succeeded, ".flac")

        if failed:
            log.error("Some songs failed to download:")
            for song in failed:
                log.error(f"  {song.name}")
