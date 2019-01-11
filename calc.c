#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#include "calc-gram.h"

#define GRAMMAR_TABLE
#include "calc-gram.h"

#define TOKEN_NAMES
#include "calc-gram.h"

static const token_t *
match_state(token_t terminal, token_t non_terminal)
{
	int	l = 0, h = (int) sizeof(parse_table) - 1;

	while (l <= h) {
		int m = (l + h) >> 1;
		while (m > l && parse_table[m-1] != TOKEN_NONE)
			m--;
		if (parse_table[m] < terminal ||
		    (parse_table[m] == terminal && parse_table[m+1] < non_terminal))
		{
			l = m + 2;
			while (l < sizeof(parse_table) - 1 && parse_table[l-1] != TOKEN_NONE)
				l++;
		} else {
			h = m - 2;
			while (h > 0 && parse_table[h-1] != TOKEN_NONE)
				h--;
		}
	}
	if (parse_table[l] == terminal && parse_table[l+1] == non_terminal)
		return &parse_table[l+2];
	return NULL;
}

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

static int lex_value;

static token_t
lex(void)
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
	    int v = c - '0';
	    for (;;) {
		c = in_c();
		if ('0' <= c && c <= '9')
		    v = v * 10 + (c - '0');
                else {
                    un_in_c(c);
                    break;
		}
	    }
            lex_value = v;
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

static token_t parse_stack[32];
static int parse_stack_p = 0;

static inline token_t
parse_pop(void)
{
    return parse_stack[--parse_stack_p];
}

static inline void
parse_push(const token_t *tokens)
{
    const token_t *t = tokens;
    while (*t != TOKEN_NONE)
	t++;
    while (t != tokens)
	parse_stack[parse_stack_p++] = *--t;
}

static inline bool
parse_empty(void)
{
    return parse_stack_p == 0;
}

static inline bool
is_terminal(token_t token)
{
    return token < FIRST_NON_TERMINAL;
}

static inline bool
is_action(token_t token)
{
    return token >= FIRST_ACTION;
}

static inline bool
is_non_terminal(token_t token)
{
    return !is_terminal(token) && !is_action(token);
}

static void
parse(void)
{
    token_t token = TOKEN_NONE;

    parse_stack_p = 0;
    value_stack_p = 0;

    parse_stack[parse_stack_p++] = NON_TERMINAL_start;

    for (;;) {
	if (token == TOKEN_NONE)
	    token = lex();

	if (parse_empty()) {
	    if (token != END)
		printf("syntax error. got %s expected %s\n",
		       token_names[token], token_names[END]);
	    return;
	}

#if 0
	{
	    int i;
	    printf("token %s stack", token_names[token]);
	    for (i = parse_stack_p-1; i >= 0; i--)
		printf(" %s", token_names[parse_stack[i]]);
	    printf("\n");
	}
#endif

	token_t top = parse_pop();

	if (is_action(top)) {
	    switch(top) {
		#define ACTIONS_SWITCH
		#include "calc-gram.h"
	    default:
		break;
	    }
	} else if (is_terminal(top)) {
	    if (top != token) {
		printf("syntax error. got %s expected %s\n", token_names[token], token_names[top]);
		return;
	    }
	    token = TOKEN_NONE;
	} else {
	    const token_t *tokens = match_state(token, top);
	    if (!tokens) {
		printf("syntax error. got %s expected %s\n", token_names[token], token_names[top]);
		return;
	    }
	    parse_push(tokens);
	}
    }
}

int main(int argc, char **argv)
{
    parse();
    return 0;
}
