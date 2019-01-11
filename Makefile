CFLAGS=-g -Wall -Wpointer-arith -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -Wnested-externs

calc: calc.c calc-gram.h
	cc $(CFLAGS) -o $@ calc.c

calc-gram.h: calc.gram lola.py lola_core.py
	python3 lola.py < calc.gram > $@

clean:
	rm -f calc calc-gram.h
