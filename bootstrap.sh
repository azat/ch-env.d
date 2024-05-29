#!/usr/bin/env bash

# Check is script had been "source"ed
function __sourced()
{
    local f
    # remove the first two elements:
    # [0] - __sourced
    unset "FUNCNAME[0]"
    # [1] - source bootstrap.sh # from other scripts
    unset "FUNCNAME[1]"
    for f in "${FUNCNAME[@]}"; do
        # Some comments for internal bash functions:
        # - "main" is the name of the function in case of script executed not sourced
        # - "source" is the name of the function in case of script sourced
        if [ "$f" == "source" ]; then
            return 0
        fi
    done
    return 1
}
export -f __sourced

__sourced || {
    cat >&2 <<EOL
Usage: source ${BASH_SOURCE[0]}
Otherwise changes will not reflect in the current shell
Or maybe you have sourced it from a "main" function within a script, in this case rename it to avoid overlaps
FUNCNAME: ${FUNCNAME[*]}
EOL
    exit 1
}
