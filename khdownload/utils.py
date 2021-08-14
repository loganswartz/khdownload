#!/usr/bin/env python3

# Imports {{{
# builtins
import subprocess
from subprocess import PIPE
import contextlib
import logging
import pathlib
import re
from typing import BinaryIO, Collection, Literal
from urllib.parse import urlparse

# 3rd party
import requests
from tqdm import tqdm

# local modules

# }}}


log = logging.getLogger(__name__)


def normalize_url(url: str, parent: str):
    """
    Convert a relative URL to an absolute one, using an existing absolute URL.
    """
    parsed = urlparse(url)

    if not parsed.netloc:
        domain = urlparse(parent)
        return parsed._replace(scheme=domain.scheme, netloc=domain.netloc).geturl()

    return url


@contextlib.contextmanager
def StreamTqdm(
    output: BinaryIO,
    input: requests.Response,
    filemode: Literal["read", "write"] = "write",
    **kwargs,
):
    """
    Convenience method for showing the progress of a stream being saved.
    """
    file_size = int(input.headers.get("Content-Length", 0))  # in bytes
    with tqdm.wrapattr(output, filemode, total=file_size, **kwargs) as pbar:
        try:
            yield pbar
        finally:
            ...


def check_disposition_filename(resp: requests.Response):
    disposition = resp.headers.get("Content-Disposition", None)
    if disposition is not None:
        regex = r"filename=\"(.+)\""
        parsed = re.search(regex, disposition)
        return parsed.group(1) if parsed else None

    return None


def convert_files(files: Collection[pathlib.Path], filetype: str, delete=True):
    """
    Convert a batch of files to a given filetype.

    The filetype should start with a period. Pass `delete=False` to keep the
    original file after converting.
    """
    num = len(files)
    type = filetype.lstrip(".")
    log.info(f"Converting {num} file{'s' if num > 1 else ''} to {type}....")

    def build_cmd(file):
        new = file.with_suffix(filetype)
        cmd = ["ffmpeg", "-i", file, "-f", type, new]
        return cmd

    tasks = {
        file: subprocess.Popen(build_cmd(file), text=True, stdout=PIPE, stderr=PIPE)
        for file in files
    }

    for file, task in tasks.items():
        task.wait()
        if delete:
            file.unlink()

    return tasks
