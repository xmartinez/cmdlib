#!/bin/bash

# Workaround for #3094. This will be unnecessary once we upgrade mypy
# to 0.800 (which fixes #8824)
#
# poetry: https://github.com/python-poetry/poetry/issues/3094
# mypy: https://github.com/python/mypy/issues/8824

main() {
    package="$1"; shift
    path="$(poetry run python -c 'import pytest; print(pytest.__path__[0])')"
    site_packages="${path%/*}"
    cp -v "${site_packages}/${package}.pth" "${site_packages}"/easy-install.pth
}

main "$@"
