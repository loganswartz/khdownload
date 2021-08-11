#!/usr/bin/env python3

# Imports {{{
# builtins
import pathlib
import sys

# 3rd party
import click

# local modules
from khdownload.download import download_album

# }}}


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
    default=pathlib.Path("."),
)
@click.option(
    "-c", "--convert-m4a", help="Convert any .m4a files to flac", is_flag=True
)
def cli(urls, list_file, output, convert_m4a):
    urls = set(urls)
    if list_file:
        urls = urls.union(
            {url.strip() for url in list_file.splitlines() if url.strip()}
        )
    if not urls:
        print("Please specify a URL.")
        sys.exit(1)

    for album_url in urls:
        download_album(album_url, folder=output)
