/*
 * Copyright © 2019 Keith Packard <keithp@keithp.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>
#include <stdlib.h>

#include "calc-gram.h"

#define PARSE_STACK_SIZE	32

static int lex_c = 0;

static int in_c(void)
{
    int c;
    if (lex_c != 0) {
        c = lex_c;
        lex_c = 0;
    } else {
	c = getchar();
    }
    return c;
}

static void un_in_c(int c)
{
    lex_c = c;
}

static double lex_value;

static token_t
lex(void *lex_context)
{
    for (;;) {
	int c = in_c();
	switch (c) {
	case EOF:
	    return END;
	case '+':
	    return PLUS;
	case '-':
	    return MINUS;
	case '*':
	    return TIMES;
	case '/':
	    return DIVIDE;
	case '(':
	    return OP;
	case ')':
	    return CP;
	case '\n':
	    return NL;
	}
	if ('0' <= c && c <= '9') {
	    char num_buf[32];
	    int num_cnt = 0;
	    while (isdigit(c)) {
		num_buf[num_cnt++] = c;
		c = in_c();
	    }
	    if (c == '.') {
		num_buf[num_cnt++] = c;
		c = in_c();
		while (isdigit(c)) {
		    num_buf[num_cnt++] = c;
		    c = in_c();
		}
	    }
	    if (c == 'e') {
		num_buf[num_cnt++] = c;
		c = in_c();
		if (c == '-' || c == '+') {
		    num_buf[num_cnt++] = c;
		    c = in_c();
		}
		while (isdigit(c)) {
		    num_buf[num_cnt++] = c;
		    c = in_c();
		}
	    }
	    num_buf[num_cnt++] = '\0';
            un_in_c(c);
            lex_value = strtod(num_buf, NULL);
            return NUMBER;
	}
    }
}

static double value_stack[32];
static int value_stack_p = 0;

static void push(double value)
{
    value_stack[value_stack_p++] = value;
}

static double pop(void)
{
    return value_stack[--value_stack_p];
}

#define GRAMMAR_TABLE
#define TOKEN_NAMES
#define PARSE_CODE
#include "calc-gram.h"

int main(int argc, char **argv)
{
    parse(NULL);
    return 0;
}
