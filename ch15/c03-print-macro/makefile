run: print
	./print.out

print: print.o libtio.a
	ld -m elf_i386 -o print.out print.o -L. -ltio

print.o: print.nasm macro.inc
	nasm -f elf32 -P"macro.inc" -o print.o print.nasm

libtio.a: tio.c
	gcc -m32 -c -o tio.o tio.c
	ar -crv libtio.a tio.o

clean:
	rm print.o print.out tio.o libtio.a
