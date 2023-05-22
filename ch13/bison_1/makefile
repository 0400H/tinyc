CC = gcc
SRC = lex.yy.c y.tab.c

calc: $(SRC)
	$(CC) -o calc $(SRC)

lex.yy.c: scanner.l
	flex $<

y.tab.c: parser.y
	bison -vdty $<

clean:
	rm -f *.o lex.yy.c y.tab.c y.tab.h y.output calc || true