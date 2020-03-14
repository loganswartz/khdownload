# khdownload
Automatically download entire albums from khinsider from the commandline.

```bash
usage: khdownload [-h] [-f FILE] [-o OUTPUT] [URL [URL ...]]

positional arguments:
  URL                   URLs of albums to download

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to a text file containing album URLs (separated
                        by newlines)
  -o OUTPUT, --output OUTPUT
                        Path specifying where the albums should be saved
```

## About
This script downloads all the songs of a particular filetype in any given album from [downloads.khinsider.com](downloads.khinsider.com). It automatically grabs the best filetype available, and shows the progress of the download as it goes. It automatically scrapes the title of the album and the songs, and downloads the songs into a folder named after the album.

## Installation
First install the required Python modules with:
```bash
~/khdownload $ pip3 install -r requirements.txt
```
To install, symlink the `khdownload` file into a location in your path, like `~/.local/bin`.
While in the cloned repo:
```bash
~/khdownload $ ln -s ~/khdownload/khdownload ~/.local/bin/khdownload
```

## Usage
```bash
# download an album
~ $ khdownload 'https://downloads.khinsider.com/game-soundtracks/album/pokemon-ruby-sapphire-music-super-complete'

# download a list of albums from a file
~ $ khdownload -f albums.txt

# save to a particular directory
~ $ khdownload -f albums.txt -o /path/to/some/dir
```
