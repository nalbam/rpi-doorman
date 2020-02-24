#!/bin/bash

OS_NAME="$(uname | awk '{print tolower($0)}')"

SHELL_DIR=$(dirname $0)

pushd ${SHELL_DIR}

git pull

python3 run.py --mirror

popd
