#!/usr/bin/bash

set -e

export BUILD_PATH=`pwd -P`/build
export TCC_PATH=$BUILD_PATH
export PATH=$TCC_PATH:$PATH
export SIM_PATH=$TCC_PATH/simulator.py

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

    CMD="$BUILD_PATH/$filenakedname-$fileext-build/$filenakedname"
    echo "exec $CMD"
    $CMD

    CMD="python3 -u $SIM_PATH -f $BUILD_PATH/$filenakedname-$fileext-build/$filenakedname.asm -a=1"
    echo $CMD
    $CMD

    echo press any key to continue...
    read -n 1
done
