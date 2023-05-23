run: print
	./print.out

print: print.o libtio.a
	ld -o print.out print.o -L. -ltio -m elf_i386 -N

print.o: print.nasm macro.inc
	nasm -f elf32 -P"macro.inc" -o print.o print.nasm

libtio.a: tio.c
	gcc -o tio.s -S tio.c -m32 -march=x86-64 -O0 -fno-pie -fno-stack-protector
	gcc -o tio.o tio.s -c -m32 -march=x86-64
	ar -crv libtio.a tio.o

clean:
	rm *.s *.o *.a *.out || true
