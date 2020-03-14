#!/usr/bin/env python3

import pathlib
import sys
import re
from urllib.parse import urlparse, unquote
import shutil
import argparse
import collections

from bs4 import BeautifulSoup
import requests
from requests.exceptions import MissingSchema
from tqdm import tqdm


def AbsolutePath(path):
    return pathlib.Path(path).expanduser().resolve()

filetype_rankings = collections.defaultdict(lambda: 100)
filetype_rankings.update({
    '.flac': 1,
    '.m4a': 2,
    '.mp3': 3,
})

def main():
    parser = argparse.ArgumentParser(prog='khdownload')
    parser.add_argument('urls', help='URLs of albums to download', nargs='*', metavar='URL')
    parser.add_argument('-f', '--file', type=AbsolutePath, help='Path to a text file containing album URLs (separated by newlines)')
    parser.add_argument('-o', '--output', help='Path specifying where the albums should be saved', type=AbsolutePath)

    args = parser.parse_args()

    args.urls = set(args.urls)
    if not args.urls and not args.file:
        print('Please specify a URL.')
        sys.exit(1)
    if args.file:
        try:
            urls = args.urls.union({url.strip() for url in args.file.open() if url.strip()})
        except FileNotFoundError:
            print('File not found.')
            sys.exit(1)
    else:
        urls = args.urls


    for url in urls:
        # scrape the album page
        resp = requests.get(url)
        scraped = BeautifulSoup(resp.text, 'html.parser')

        title = scraped.find(id='EchoTopic').find('h2').text
        songs = {a.get('href') for a in scraped.find(id='songlist').find_all('a')}
        songs = sorted(songs, key=lambda song: unquote(pathlib.Path(song).name))
        if not songs:
            print('No songs found!')
            continue

        dl_folder = pathlib.Path(title)
        if args.output:
            dl_folder = args.output / dl_folder

        try:
            dl_folder.mkdir()
        except FileExistsError:
            print(f"A folder called \"{dl_folder.name}\" already exists.")
            continue

        print(f"Downloading {title}....")
        for song_page in tqdm(songs, unit='files', ncols=90, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {unit}'):
            try:
                page = requests.get(song_page)
            except MissingSchema:   # add the FQDN if it's a relative path
                parsed_url = urlparse(url)
                page = requests.get(f"{parsed_url.scheme}://{parsed_url.netloc}/{song_page}")

            # get the raw list of available files for download
            song_scraped = BeautifulSoup(page.text, 'html.parser')
            files = {a.parent.get('href') for a in song_scraped.find_all(class_='songDownloadLink')}

            # choose which filetype to download
            try:
                file = sorted(files, key=lambda file: filetype_rankings[pathlib.Path(file).suffix])[0]
            except KeyError:
                tqdm.write(f"    Error: no files found on {song_page}.")
                continue

            # extract filename from url and decode from url encoding
            local_filename = pathlib.Path(unquote(file)).name
            tqdm.write(f"    Downloading {local_filename}...")

            local_file = dl_folder / local_filename

            # likely more efficient method of saving the files, albeit without a progress bar
            # with requests.get(file, stream=True) as data:
            #     with pathlib.Path(local_file).open('wb') as f:
            #         shutil.copyfileobj(data.raw, f)

            with pathlib.Path(local_file).open('wb') as f:
                with requests.get(file, stream=True) as stream:
                    file_size = int(stream.headers['Content-Length'])   # in bytes
                    pbar_options = {
                            'total': file_size,
                            'unit': 'B',
                            'unit_scale': True,
                            'unit_divisor': 1024,
                            'ncols': 90,
                            'bar_format': '{l_bar}{bar}| {percentage:.0f}% | {total_fmt}{unit} | {rate_fmt}',
                            'leave': False,
                    }
                    with tqdm(**pbar_options) as pbar:
                        for chunk in stream.iter_content(chunk_size=1024*8):   # chunk_size=None means whatever size they come in as
                            f.write(chunk)
                            pbar.update(len(chunk))

