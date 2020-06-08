#!/bin/bash
set -euo pipefail

http_fetch() {
    local output="$1"; shift
    local url="$1"; shift
    echo "FETCH ${url} -> ${output}"
    curl --fail --silent --show-error --globoff --location --output "${output}" "${url}"
}

main() {
    local root="$1"; shift
    local version="$1"; shift
    local arch="$1"; shift

    local tmp="/tmp/poetry.tar.gz"
    local url="https://github.com/python-poetry/poetry/releases/download/${version}/poetry-${version}-${arch}.tar.gz"

    install -v -d "${root}"

    install -v -d "${root}/lib"
    http_fetch "${tmp}" "${url}"
    tar -C "${root}/lib" -xzf "${tmp}"

    install -v -d "${root}/bin"
    <<EOF install -T -m 755 /dev/stdin "${root}/bin/poetry"
#!/usr/bin/env python3
import sys
import os.path

lib = os.path.expanduser("${root}/lib")
sys.path.insert(0, lib)

if __name__ == "__main__":
    from poetry.console import main

    main()
EOF
}

main "$@"
