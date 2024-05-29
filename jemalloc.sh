#!/usr/bin/env bash

source "$(dirname "${BASH_SOURCE[0]}")/bootstrap.sh"

function main()
{
    export MALLOC_CONF=abort_conf:true
}
main "$@"
