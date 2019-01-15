# Lola — an LL parser table generator

Lola is a parser generator along the lines of yacc or bison, but
instead of handling LALR grammars, it only supports LL grammars. This
simplification makes the resulting parser much smaller, but of course
is only suitable if the target language is actually LL.

Lola was originally written over thirty years ago in a long-lost
dialect of lisp called Kalypso. I've transliterated it into python,
but I haven't tried to make it look like reasonable code.

## Input Syntax

The original kalypso version just used lists for the input. Python
doesn't exactly make that easy to manage, so I create a simple parser
(written in python data structures), and a python parser engine to
generate suitable data structures from a more usable input format
which looks much like yacc. I've used the grammar of the input format
to demonstrate the input format:

	start		: non-term start
			|
			;
	non-term	: SYMBOL @NONTERM@ COLON rules @RULES@ SEMI
			;
	rules		: rule rules-p
			;
	rules-p		: VBAR rule rules-p
			|
			;
	rule		: symbols @RULE@
			;
	symbols		: SYMBOL @SYMBOL@ symbols
			|
			;

## Actions

Instead of assuming C syntax for actions with matching curly braces,
actions are just sequences of characters bounded by @ signs, to
include a literal @ within the action, just use two @ signs. The goal
is to let you use lola with any language by creating a new parser
framework and inserting the actions as appropriate. Each parser can do
whatever is appropriate with the contents of the actions.

## Parser Operation

The generated parse tables map a (terminal, non-terminal) pair into
one of the productions in the grammar. The parser has two pieces of
state -- a stack of tokens and a current input terminal. The parser
works as follows:

 1) If the parse stack is not empty, pop an entry from the parse
    stack, call it 'top'.

 2) If 'top' is an action, then execute it and go back to 1)

 3) If we don't have an input token, read one from the lexer, call
    this 'token'

 4) If 'token' is end-of-file, then check if the parse stack is
    empty. If so, we're done. Otherwise, we have a syntax error.

 5) If 'top' is a terminal, then check if it matches 'token'. If so,
    discard 'token' and go back to 1).

 6) Otherwise, 'top' must be a non-terminal. Check in the parse table
    for and entry matching ('token', 'top'). If one exists, push the
    resulting production tokens on the stack and go back to
    1). Otherwise, we have a syntax error.

Note that 'actions' are executed *before* a token is read from
input. This allows them to operate on the just-matched input token
value, and also at end-of-file.

## C Framework

The current C output code generates a header file that defines the
tokens, specifies a parser that includes the actions as case elements
of a switch statement. All of this is generated in a single C header
file, which makes incorporating it into build system straightforward.

### The Generated C Header

The header file has four parts. Each part is protected by #ifdefs, so
this single header file can be used multiple times, extracting the
desired information by selecting the desired bits.

 1) An enum containing all of the tokens used in the grammar,
    terminals non-terminals and actions. This is to be used by the
    lexer to pass terminals into the parser. All of the terminals are
    spelled as they appeared in the grammar. Non-terminals are
    prefixed by 'NON_TERMINAL_', actions are 'ACTION_' followed by a
    number. Both of those shouldn't be used outside of the parser
    itself. In all cases, '-' characters are replaced by '_'. This
    section is selected when no #defines naming other sections are specified.

 2) The parse tables. This section is selected with #define GRAMMAR_TABLE

 3) An array of token names, indexed by token value. This is useful
    when debugging a grammar during development. This section is
    selected with #define TOKEN_NAMES

 4) The parser. This is a pile of C code which uses the other data
    from the file to parse input. This section is selected with
    #define PARSE_CODE

Actions in the parser are expected to be C fragments and are inserted
into the body of the parse function.

The parse function is declared as:

	typedef enum {
	    parse_return_success,
	    parse_return_syntax,
	    parse_return_end,
	    parse_return_oom,
	} parse_return_t;

	token_t
	lex(void *lex_context);

	static parse_return_t
	parse(void *lex_context);

It passes the 'lex_context' value to the lex function, which must be
declared by the enclosing application.

### Building a C Parser

Here's an outline of a C parser. For this example, assume that the
name of the generated header file is 'test-gram.h'.

	#include "test-gram.h"
	
	#define PARSE_STACK_SIZE	32
	
	static token_t
	lex(void *lex_context) { ... }

	#define GRAMMAR_TABLE
	#define PARSE_CODE
	#include "test-gram.h"
	
	bool my_parser(void) { return parse(NULL) == parse_return_success; }

If you add a '#define PARSE_DEBUG' before including the parse code,
then the parser operation will be printed to stdout during
operation. This code uses the token names, and so you will also need
to add '#define TOKEN_NAMES' as well.

## Calculator Example

This repository includes a simple 4-function calculator example that
demonstrates how to interpret the parse tables and use the rest of the
generated header file.

## Future Ideas

While lola is already useful, I've got some ideas on how to improve
it.

### Automatic Grammar Transformations

One of the restrictions of the current parser is that the selection of
a production can only depend on the current input token and
non-terminal on the top of the stack. This often requires inserting
additional non-terminals and productions into the grammar. There are a
set of grammar transformations which can be applied automatically to
simpify writing lola grammars.

The kalypso code includes a tool called 'flo' which does
left-common-subexpression factoring. That might be an interesting
place to start.

### Better Error Detection

Lola does only limited checking of the specified language; many non-LL
languages can be specified and will generate output. Of course, the
resulting output will only recognize an LL language related (in some
way) to the desired language. Incorporating additional checks within
lola to validate the input would help avoid errors here.

### Synthetic Attribute Tracking

Actions within a lola grammar get no help from the parser with
managing attributes. In yacc, each token in a production is assigned
an attribute value, making writing actions much clearer and more
straightforward. I'd like to do something similar in lola. I think
this would involve creating an attribute stack and then decorating the
parse tables with implicit actions to manage that during evaluation of
the parse tables, pushing values as tokens in the production are
processed, and popping a list of values when the final token for a
production is handled.
