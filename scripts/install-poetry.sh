#!/bin/bash
set -euo pipefail

install_uv() {
    local version="$1"; shift
    local arch
    arch=$(uname -m)

    local basename=uv-${arch}-unknown-linux-gnu
    local url=https://github.com/astral-sh/uv/releases/download/${version}/${basename}.tar.gz

    mkdir -p ~/.local/bin
    curl -sSfL "${url}" |
        tar -O -xzf - "${basename}"/uv |
        install /dev/stdin ~/.local/bin/uv
}

main() {
    local version="$1"; shift

    install_uv 0.4.19
    uv tool install poetry=="${version}"
}

main "$@"
