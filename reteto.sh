#!/usr/bin/env bash

repo=$1
pwd=$PWD

DIR=$(mktemp -d reteto.XXXXXX)
pushd $DIR
    git clone --depth 1 $repo $DIR
    mkdir target
    python3 $pwd/reteto.py | tee target/reteto.log
popd