run: test
	./test.out

test: test.o libtio.a
	ld -m elf_i386 -o test.out test.o -L. -ltio

test.o: test.nasm macro.inc
	nasm -f elf32 -P"macro.inc" -o test.o test.nasm

libtio.a: tio.c
	gcc -m32 -c -o tio.o tio.c
	ar -crv libtio.a tio.o

clean:
	rm test.o test.out tio.o libtio.a
