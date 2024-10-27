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
#include <string.h>

#include "json-gram.h"

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

static char *lex_value;

static bool
lexadd(char c)
{
    size_t len = lex_value ? strlen(lex_value) : 0;
    lex_value = realloc(lex_value, len + 2);
    if (!lex_value)
	return false;
    lex_value[len] = c;
    lex_value[len+1] = '\0';
    return true;
}

static token_t
lex(void *lex_context)
{
    if (!lex_value)
	lex_value = malloc(1);
    lex_value[0] = '\0';
    for (;;) {
	int c = in_c();
	switch (c) {
	case EOF:
	    return END;
	case '{':
	    return OC;
	case '}':
	    return CC;
	case '[':
	    return OS;
	case ']':
	    return CS;
	case ',':
	    return COMMA;
	case ':':
	    return COLON;
	case '\n':
	case ' ':
	case '\t':
	    continue;
	case '"':
	    for (;;) {
		c = in_c();
		if (c == '"')
		    break;
		if (c == '\\') {
		    c = in_c();
		    switch (c) {
		    case 'b':
			c = '\b';
			break;
		    case 'f':
			c = '\f';
			break;
		    case 'n':
			c = '\n';
			break;
		    case 'r':
			c = '\r';
			break;
		    case 't':
			c = '\t';
			break;
		    default:
			break;
		    }
		}
		if (!lexadd(c))
		    return END;
	    }
	    return STRING;
	case '0': case '1': case '2': case '3':	case '4':
	case '5': case '6': case '7': case '8':	case '9':
	    while (isdigit(c)) {
		if (!lexadd(c))
		    return END;
		c = in_c();
	    }
	    if (c == '.') {
		if (!lexadd(c))
		    return END;
		c = in_c();
		while (isdigit(c)) {
		    if (!lexadd(c))
			return END;
		    c = in_c();
		}
	    }
	    if (c == 'e') {
		if (!lexadd(c))
		    return END;
		c = in_c();
		if (c == '-' || c == '+') {
		    if (!lexadd(c))
			return END;
		    c = in_c();
		}
		while (isdigit(c)) {
		    if (!lexadd(c))
			return END;
		    c = in_c();
		}
	    }
            un_in_c(c);
	    return NUMBER;
	default:
	    while (islower(c)) {
		if (!lexadd(c))
		    return END;
		c = in_c();
	    }
	    un_in_c(c);
	    if (!strcmp(lex_value, "true"))
		return TRUE_TOKEN;
	    if (!strcmp(lex_value, "false"))
		return FALSE_TOKEN;
	    if (!strcmp(lex_value, "null"))
		return NULL_TOKEN;
	}
    }
}

typedef struct value value_t;
typedef struct object object_t;
typedef struct array array_t;

typedef enum {
	value_object, value_array, value_string, value_number, value_bool, value_null
} value_type;

struct value {
    value_type	type;
    union {
	object_t	*object;
	array_t		*array;
	char		*string;
	double		number;
	bool		boolean;
    };
};

typedef struct {
    char	*name;
    value_t	value;
} member_t;

struct object {
    size_t	size;
    member_t	members[];
};

struct array {
    size_t	size;
    value_t	values[];
};

static value_t value_stack[32];
static int value_stack_p = 0;

static void dump_value(int id, value_t value);

static void push(value_t value)
{
    value_stack[value_stack_p++] = value;
}

static value_t pop(void)
{
    value_t value = value_stack[--value_stack_p];
    return value;
}

static void push_null(void)
{
    push((value_t) { .type = value_null });
}

static void push_bool(bool boolean)
{
    push((value_t) { .type = value_bool, .boolean = boolean });
}

static void push_array(void)
{
    push((value_t) { .type = value_array, .array = calloc(sizeof(array_t), 1) });
}

static void push_object(void)
{
    push((value_t) { .type = value_object, .object = calloc(sizeof(object_t), 1) });
}

static void push_string(const char *s)
{
    push((value_t) { .type = value_string, .string = strdup(s) });
}

static void push_number(double d)
{
    value_t value = { .type = value_number, .number = d };
    push(value);
}

static void add_array(value_t value)
{
    array_t *a = pop().array;

    a = realloc(a, sizeof(array_t) + (a->size + 1) * sizeof(value_t));
    a->values[a->size++] = value;
    push((value_t) { .type = value_array, .array = a });
}

static void add_object(const char *name, value_t value)
{
    object_t *o = pop().object;

    o = realloc(o, sizeof(object_t) + (o->size + 1) * sizeof(member_t));
    o->members[o->size++] = (member_t) {
	.name = strdup(name),
	.value = value
    };
    push((value_t) { .type = value_object, .object = o });
}

static void indent (int id)
{
    while (id--)
	printf("    ");
}

static void dump_object(int id, object_t *object)
{
    size_t i;
    printf("{\n");
    id++;
    for (i = 0; i < object->size; i++) {
	indent(id);
	printf("\"%s\": ", object->members[i].name);
	dump_value(id, object->members[i].value);
	if (i < object->size - 1)
	    printf(",");
	printf("\n");
    }
    id--;
    indent(id);
    printf("}\n");
}

static void dump_array(int id, array_t *array)
{
    size_t i;
    printf("[\n");
    id++;
    for (i = 0; i < array->size; i++) {
	indent(id);
	dump_value(id, array->values[i]);
	if (i < array->size - 1)
	    printf(",");
	printf("\n");
    }
    id--;
    indent(id);
    printf("}");
}

static void dump_value(int id, value_t value)
{
    indent(id);
    switch (value.type) {
    case value_object:
	dump_object(id, value.object);
	break;
    case value_array:
	dump_array(id, value.array);
	break;
    case value_string:
	printf("\"%s\"", value.string);
	break;
    case value_number:
	printf("%.17g", value.number);
	break;
    case value_bool:
	printf("%s", value.boolean ? "true" : "false");
	break;
    case value_null:
	printf("null");
	break;
    }
}

#define GRAMMAR_TABLE
#define TOKEN_NAMES
#define PARSE_CODE
#include "json-gram.h"

int main(int argc, char **argv)
{
    if (parse(NULL) == parse_return_success) {
	dump_value(0, pop());
	printf("\n");
    }
    return 0;
}
