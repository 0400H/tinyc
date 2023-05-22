#!/bin/bash

set -e

export BUILD_PATH=build
export TCC_PATH=$BUILD_PATH
export PATH=$TCC_PATH:$PATH

for src in $(ls samples/*.c)
do
    filename=${src%.*}
    fileext=${src##*.}
    filenakedname=${filename##*/}
    objdir=$filename-$fileext-build

    clear

    echo "build $src"
    tcc $src

    rm -rf $BUILD_PATH/$filenakedname-$fileext-build || true
    mv $objdir $BUILD_PATH

    echo "exec $BUILD_PATH/$filenakedname-$fileext-build/$filenakedname"
    $BUILD_PATH/$filenakedname-$fileext-build/$filenakedname

    echo press any key to continue...
    read -n 1
done
