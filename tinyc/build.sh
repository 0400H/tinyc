#!/bin/bash

set -e

mkdir -p build

cd build

flex ../sources/scanner.l
bison -vdty ../sources/parser.y
gcc -o tcc-frontend lex.yy.c y.tab.c
# rm -f y.* lex.*

gcc -fno-stack-protector -m32 -c -o tio.o ../sources/tio.c
ar -crv libtio.a tio.o > /dev/null
# rm -f tio.o

cp ../sources/{macro.inc,pysim.py,tcc,pysimulate} .
chmod u+x tcc tcc-frontend pysimulate

cd -
