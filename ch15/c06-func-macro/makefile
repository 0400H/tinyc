run: test
	./test.out

test: test.o libtio.a
	ld -o test.out test.o -L. -ltio -m elf_i386 -N

test.o: test.pcode test.funcmacro macro.inc
	nasm -f elf32 -P"macro.inc" -P"test.funcmacro" -o test.o test.pcode

libtio.a: tio.c
	gcc -o tio.s -S tio.c -m32 -march=x86-64 -O0 -fno-pie -fno-stack-protector
	gcc -o tio.o tio.s -c -m32 -march=x86-64
	ar -crv libtio.a tio.o

clean:
	rm *.s *.o *.a *.out || true
