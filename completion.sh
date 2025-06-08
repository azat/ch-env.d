#!/usr/bin/env bash

source "$(dirname "${BASH_SOURCE[0]}")/bootstrap.sh"

# Add clickhouse completion into $BASH_COMPLETION_USER_FILE
# (see /usr/share/bash-completion/bash_completion)
function main()
{
    function ensure_line()
    {
        local f=$1 && shift
        local l=$1 && shift
        grep -q "$@" "$l" "$f" || {
            echo "$l" >> "$f"
        }
    }

    touch "$BASH_COMPLETION_USER_FILE"

    local f
    for f in "$CLICKHOUSE_SRC_PATH"/programs/bash-completion/completions/*; do
        if [[ $f =~ .*CMakeLists.txt ]]; then
            continue
        fi
        ensure_line "$BASH_COMPLETION_USER_FILE" "source $f" -x
    done
}
main "$@"
