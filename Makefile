#
# Copyright © 2019 Keith Packard <keithp@keithp.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#

CFLAGS=-g -O2 -I. -Wall -Wpointer-arith -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -Wnested-externs

PREFIX=$(DESTDIR)/usr/local
BINDIR = $(PREFIX)/bin

all: lola calc pycalc

lola: lola.py
	cp lola.py lola
	chmod +x lola

calc: calc.c calc-gram.h
	cc $(CFLAGS) -o $@ calc.c

calc-gram.h: calc-gram.ll lola
	python3 ./lola.py -o $@ calc-gram.ll

pycalc: pycalc.py pycalc_gram.py
	cp pycalc.py $@
	chmod +x pycalc

pycalc_gram.py: pycalc_gram.ll lola
	python3 ./lola.py -o $@ --format=python pycalc_gram.ll

install: lola
	install lola $(BINDIR)

clean:
	rm -f lola calc pycalc calc-gram.h pycalc_gram.py
