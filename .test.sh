#!/usr/bin/env bash

function test_ok() { echo OK; }
failed_tests=0
function test_fail()
{
    echo KO
    (( ++failed_tests ))
}

mapfile -t files < <(find . -maxdepth 1 -mindepth 1 -type f -name '*.sh' -and '!' -name '.*' -and '!' -name 'bootstrap.sh')
echo "Files: ${files[*]}"

# stderr is usually redirected to /dev/null, change output of bash -x to stdout
BASH_XTRACEFD=1

for file in "${files[@]}"; do
    echo -n "$(basename $file) sourceable: "
    bash -c "source $file" && test_ok || test_fail
done

for file in "${files[@]}"; do
    echo -n "$(basename $file) is not invokable: "
    bash "$file" 2>/dev/null && test_fail || test_ok
done

if [ "$failed_tests" -gt 0 ]; then
    echo "Failed tests: $failed_tests" >&2
    exit 1
fi
