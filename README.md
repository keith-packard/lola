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
	non-term	: @NONTERM@ SYMBOL COLON rules @RULES@ SEMI
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
framework and inserting the actions as appropriate.

## C Framework

The current C output code generates a header file that defines the
tokens, specifies the parse table and includes the actions as case
elements of a switch statement.

## Calculator Example

This repository includes a simple 4-function calculator example that
demonstrates how to interpret the parse tables and use the rest of the
generated header file.
