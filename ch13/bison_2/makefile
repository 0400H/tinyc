CC = gcc
OUT = calc
SRC = lex.yy.c y.tab.c
SCANNER = scanner.l
PARSER = parser.y

build: $(OUT)

run: $(OUT)
	./$(OUT) < test.c > test.asm

clean:
	rm -f *.o lex.yy.c y.tab.c y.tab.h y.output $(OUT) || true

$(OUT): $(SRC)
	$(CC) -o $(OUT) $(SRC)

lex.yy.c: $(SCANNER)
	flex $<

y.tab.c: $(PARSER)
	bison -vdty $<
