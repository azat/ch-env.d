#!/usr/bin/env -S PYTHONHASHSEED=0 python3

# Highlight kafka debug logs:
#
#     kafka debug cgrp,consumer,topic,protocol
#
# Usage example:
#
#   kafkalog.py < kafka.log | less -R

import sys
import signal
from datetime import datetime

# Copied from clickhouse/base/common/terminalColors.cpp
def setColor(hash_):
    # Make a random RGB color that has constant brightness.
    # https://en.wikipedia.org/wiki/YCbCr

    # Note that this is darker than the middle relative luminance, see
    # "Gamma_correction" and "Luma_(video)".
    # It still looks awesome.
    y = 128

    cb = hash_ % 256
    cr = hash_ / 256 % 256

    r = int(max(0.0, min(255.0, y + 1.402 * (cr - 128))))
    g = int(max(0.0, min(255.0, y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128))))
    b = int(max(0.0, min(255.0, y + 1.772 * (cb - 128))))

    # ANSI escape sequence to set 24-bit foreground font color in terminal.
    return '\033[38;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm'

def resetColor():
    return '\033[0m'

def highlight(str_, key_=None):
    if key_ is None:
        key_ = str_
    return setColor(hash(key_)) + str_ + resetColor()

# Possible log messages:
#
#   %7|1588388678.335|CGRPTERM|ClickHouse 20.4.1.1#consumer-2| [thrd:main]: ...
def parseMessage(line):
    parts = line.split('|')
    try:
        return {
            # parts[0]
            'timestamp': parts[1],
            'type'     : parts[2],
            'consumer' : parts[3],
            'message'  : ' '.join(parts[4:]),
        }
    except: # pylint: disable=bare-except
        # It is not enough to check length of the parts,
        # since it can have enough parts, but won't be parsed.
        return line

# Example output:
#
#   2020-05-01 23:04:00.372000|CGRPTERM|ClickHouse 20.4.1.1#consumer-2| [thrd:main]: ...
def highlightMessage(parts):
    # unhandled
    if isinstance(parts, str):
        print(parts)
        return

    # int(float()) - drop milliseconds
    # hash(str())  - distinguish colors for adjacent seconds
    ts = float(parts['timestamp'])
    timestamp_key = hash(str(int(ts)))
    timestamp_val = str(datetime.fromtimestamp(ts))
    line = '|'.join([
        highlight(timestamp_val, timestamp_key),
        highlight(parts['type']),
        highlight(parts['consumer']),
        parts['message'],
    ])
    print(line)

def main():
    it = map(str.strip, sys.stdin)
    it = map(parseMessage, it)
    it = map(highlightMessage, it)
    any(it)

if __name__ == '__main__':
    try:
        main()
    # like regular program exits (libc)
    except BrokenPipeError:
        sys.exit(128 + signal.SIGPIPE)
    except KeyboardInterrupt:
        sys.exit(128 + signal.SIGINT)
