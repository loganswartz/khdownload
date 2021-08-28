# khdownload
Automatically download entire albums from khinsider from the commandline.

```bash
Usage: khdownload [OPTIONS] [URLS]...

Options:
  -f, --from-file FILENAME  Path to a text file containing album URLs
                            (separated by newlines)
  -o, --output DIRECTORY    Path specifying where the albums should be saved
  -t, --type TEXT           Download a specific filetype
  -c, --convert-m4a         Convert any .m4a files to .flac
  -h, --help                Show this message and exit.
```

## About
This script downloads all the songs of a particular filetype in any given album
from [downloads.khinsider.com](downloads.khinsider.com). It automatically grabs
the best filetype available, and shows the progress of the download as it goes.
It automatically scrapes the title of the album and the songs, and downloads
the songs into a folder named after the album.

## Installation
```bash
git clone git@github.com:loganswartz/khdownload.git && pip3 install khdownload
```

## Usage
```bash
# download an album
~ $ khdownload 'https://downloads.khinsider.com/game-soundtracks/album/dai-gyakuten-saiban-naruhodou-ryuunosuke-no-bouken-gekiban-ongaku-daizenshuu-2015'

# download a list of albums from a file
~ $ khdownload -f ace_attorney_albums.txt

# save all the given albums in another directory
~ $ khdownload -f ace_attorney_albums.txt -o '/mnt/media/soundtracks/Ace Attorney Sountracks'
```
