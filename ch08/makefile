run: word-spliter
	./word-spliter < word-spliter.l
	echo "123qwer" | ./hide-digits

word-spliter: word-spliter.l
	flex $<
	gcc -o $@ lex.yy.c

hide-digits: hide-digits.l
	flex $<
	gcc -o $@ lex.yy.c
