#!/bin/bash

set -e

mkdir -p build

cd build

flex ../sources/scanner.l
bison -vdty ../sources/parser.y
gcc -o tcc-frontend lex.yy.c y.tab.c
# rm -f y.* lex.*

gcc -o tio.o ../sources/tio.c -c -m32 -march=x86-64 -O0 -fno-pie -fno-stack-protector
ar -crv libtio.a tio.o > /dev/null
# rm -f tio.o

cp ../sources/{macro.inc,simulator.py,tcc} .
chmod +x tcc tcc-frontend simulator.py

cd -
