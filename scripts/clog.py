#!/usr/bin/env -S PYTHONHASHSEED=0 python3

# pylint: disable=line-too-long

# Highlight (thread, query_id, level) in the clickhouse logs,
# like the server/client does in case stdout is terminal.
#
# Usage example:
#
#   clog.py < /var/log/clickhouse-server/clickhouse-server.log | less -R
#
# Difference with clickhouse-server/clickhouse-client:
#   - thread uses intHash64
#   - query_id/source uses std::hash (on server) and StringRefHash on client
# So as you can see client/server uses different hashing algorithm for strings
# (this is due to StringRefHash does not requires constructing temporary
# string, while specialization std::hash<const char *> is just a hash for
# pointer), hence this script will not care about matching hashes either (to
# match colors).
#
# NOTE: it requires terminal with 256 bit coloring

import sys
import signal

# Copied from clickhouse/base/common/terminalColors.cpp
priorityColor = {
    'Fatal'       : '\033[1;41m',
    'Critical'    : '\033[7;31m',
    'Error'       : '\033[1;31m',
    'Warning'     : '\033[0;31m',
    'Notice'      : '\033[0;33m',
    'Information' : '\033[1m',
    'Debug'       : '',
    'Trace'       : '\033[2m',
}

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

def setColorForLogPriority(priority: str):
    return priorityColor.get(priority, '')

def resetColor():
    return '\033[0m'

def highlight(str_):
    str_ = str(str_)
    return setColor(hash(str_)) + str_ + resetColor()

# Possible log messages:
#
#   YYYY.MM.DD HH:MM:SS.MS [ thread ] {query_id} <priority> ...
#   stacktrace frame
def parseMessage(line):
    parts = line.split(' ')
    try:
        line_parsed = {
            'date'     : ' '.join(parts[0:2]),
            # parts[2] == "["
            'thread'   : int(parts[3]),
            # parts[4] == "]"
            'query_id' : parts[5].strip('{}'),
            'priority' : parts[6].strip('<>'),
            'message'  : ' '.join(parts[7:]),
        }
        message_parsed = line_parsed['message'].split(':')
        line_parsed['source']  = message_parsed[0]
        line_parsed['message'] = ':'.join(message_parsed[1:])
        return line_parsed
    except: # pylint: disable=bare-except
        # It is not enough to check length of the parts,
        # since it can have enough parts, but won't be parsed.
        return line
def highlightMessage(parts):
    # Unhandled (stacktrace, ...)
    if isinstance(parts, str):
        print(parts)
        return

    line = ' '.join([
        parts['date'],
        '[ {} ]'.format(highlight(parts['thread'])),
        '{{{}}}'.format(highlight(parts['query_id'])),
        '<{}{}{}>'.format(setColorForLogPriority(parts['priority']), parts['priority'], resetColor()),
        '{}'.format(highlight(parts['source'])),
    ])
    line += ':' + parts['message']
    print(line)

def main():
    # XXX: accept bytes?
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
