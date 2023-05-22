run: hello
	./hello.out

hello: hello.nasm macro.inc
	nasm -f elf32 -o hello.o hello.nasm
	ld -m elf_i386 -o hello.out hello.o

clean:
	rm hello.o hello.out