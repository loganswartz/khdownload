#!/usr/bin/env python3

# Imports {{{
# builtins
import collections

# }}}


DEFAULT_WEIGHTS = collections.defaultdict(lambda: 0)
DEFAULT_WEIGHTS.update(
    {
        ".flac": 30,
        ".m4a": 20,
        ".mp3": 10,
    }
)
