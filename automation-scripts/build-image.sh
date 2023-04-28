#!/bin/bash

MODELS_DIR=$1
VOCABS_DIR=$2
VERSION=2.1.0

DOCKER_PROJECT=..

mkdir ../model
mkdir ../vocabs
cp $MODELS_DIR/* ../model
cp $VOCABS_DIR/* ../vocabs
docker build -t cuni-multilingual-translation-service:${VERSION} --build-arg VERSION=${VERSION} ${DOCKER_PROJECT}
rm -r ../model
rm -r ../vocabs
