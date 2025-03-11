#!/usr/bin/env bash

source "$(dirname "${BASH_SOURCE[0]}")/bootstrap.sh"

function configure_toolchain()
{
    local e=(
        UBSAN_OPTIONS=print_stacktrace=1

        ASAN_SYMBOLIZER_PATH=/bin/llvm-symbolizer
        TSAN_SYMBOLIZER_PATH=/bin/llvm-symbolizer
        UBSAN_SYMBOLIZER_PATH=/bin/llvm-symbolizer
        LLVM_SYMBOLIZER_PATH=/bin/llvm-symbolizer
        MSAN_SYMBOLIZER_PATH=/bin/llvm-symbolizer

        #RUST_BACKTRACE=full

        # This is for rust-analyzer, since ClickHouse uses clang
        CC=clang
        CXX=clang++

        TSAN_OPTIONS="external_symbolizer_path=/bin/llvm-symbolizer"
    )
    export "${e[@]}"
}

# Run ninja by default with +100 priority to not affect other processes, like:
# - desktop
# - editor + completion
function ninja()
{
    command nice -n100 ninja "$@"
}
export -f ninja

function cmake()
{
    # See also debug-build-cache.cmake
    local opts=(
        -DPARALLEL_COMPILE_JOBS=$(nproc)
        -DOMIT_HEAVY_DEBUG_SYMBOLS=OFF
        -DENABLE_BUILD_PATH_MAPPING=OFF
        -DDISABLE_OMIT_FRAME_POINTER=ON
        # due to omit frame pointers it can bail earlier
        -DCHECK_LARGE_OBJECT_SIZES=OFF
    )
    command cmake "${opts[@]}" "$@"
}
export -f cmake

function gdb()
{
    local RTMIN
    RTMIN="$(kill -l SIGRTMIN)"

    local o=(
        -q
        -ex 'set history filename ~/.gdb_history.ch'
        -ex 'set history save'
        -ex 'set history expansion on'
        # Set location to sources, since we have the following for reproducible builds:
        #
        #     -ffile-prefix-map=${CMAKE_SOURCE_DIR}=.")
        #
        # You can debug it with the following:
        #
        #     (gdb) info source
        #
        # Examples:
        # - set substitute-path /src /home/azat/ch/clickhouse
        -ex "set substitute-path . $CLICKHOUSE_SRC_PATH"
        # Ignore resize
        -ex "handle SIGWINCH pass noprint nostop"
        # NOTE: that noprint doesn't help with performance, i.e. program under
        # gdb will still work very slow in case of tons of signals sent.
        #
        # Ignore query_profiler_real_time_period_ns signal
        -ex "handle SIGUSR1 pass noprint nostop"
        # Ignore query_profiler_cpu_time_period_ns signal
        -ex "handle SIGUSR2 pass noprint nostop"
        # Ignore system.stack_trace signal
        -ex "handle $RTMIN pass noprint nostop"
    )
    command gdb "${o[@]}" "$@"
}
export -f gdb

function lldb()
{
    local o=(
        # Set location to sources, since we have the following for reproducible builds:
        #
        #     -ffile-prefix-map=${CMAKE_SOURCE_DIR}=.")
        #
        # You can debug it with the following:
        #
        #     (lldb) image lookup -v -F DB::Block::insert
        #
        # Examples:
        # - settings set target.source-map /bld /ch
        -O "settings set target.source-map .cmake $CLICKHOUSE_SRC_PATH"
        # NOTE: This will not work w/o target:
        #
        #     (lldb) process handle -p true -s false SIGWINCH
        #     error: invalid target, create a target using the 'target create' command
    )

    # Only on attach, otherwise it is tricky
    local OPTERR OPTARG OPTIND c pid
    while getopts ":p:" c; do
        case "$c" in
            p) pid="$OPTARG";;
            *) break;;
        esac
    done
    shift $((OPTIND-1))

    local RTMIN
    RTMIN="$(kill -l SIGRTMIN)"

    if [ -n "$pid" ]; then
        o+=(
            # And do a manual attach, since the following does not work,
            # because lldb first executes other commands and the attach, and
            # produce an error.
            #
            #     lldb -p PID -O "process handle -p false -s false SIGUSR2"
            -O "process attach --pid $pid"

            #
            # You can also use "env --ignore-signal=SIGWINCH clickhouse-server ..." to overcome this.
            #
            # Ignore resize
            -O "process handle -p false -s false SIGWINCH"
            # Ignore query_profiler_real_time_period_ns signal
            -O "process handle -p true -s false -n false SIGUSR1"
            # Ignore query_profiler_cpu_time_period_ns signal
            -O "process handle -p true -s false -n false SIGUSR2"
            # Ignore system.stack_trace signal
            -O "process handle -p true -s false -n false $RTMIN"
        )
        command lldb "${o[@]}" "${args[@]}" "$@"
        return
    fi

    command lldb "${o[@]}" "$@"
}
export -f lldb

function ctags()
{
    local o=(
        --recurse
        --exclude=.contrib/*
        --exclude=.cmake*
    )
    command ctags "${o[@]}" "$@"
}
export -f ctags

function main()
{
    configure_toolchain
}
main "$@"
