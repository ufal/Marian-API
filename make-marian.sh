#!/bin/bash

set -e
set -x

if [ -d ./build/ ]; then rm -r ./build/; fi
mkdir build
cd build

cmake .. \
    -DCOMPILE_CPU=on \
    -DCOMPILE_CUDA=off \
    -DCOMPILE_SERVER=on \
	-DUSE_SENTENCEPIECE=on \
    -DUSE_STATIC_LIBS=on
make -j 6
