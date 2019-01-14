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
#
# The parser operation is table driven -- the parse table
# is a set of mappings from (terminal,non-terminal) to (token ...),
# with (token ...) including terminals, non-terminals and actions.
#
# There is a parse stack of tokens. Depending on the type of the token on the 
# top of the parse stack, three different actions are taken.
#
# 1) When the top of the parse stack is a non-terminal, it is replaced
#    by the contents of the parse table entry cooresponding to the
#    current input terminal and top of stack non-terminal
#
# 2) When the top of the parse stack is a terminal, it must match
#    the current input terminal. The top of stack is discarded and
#    another input token read.
#
# 3) When the top of the parse stack is an action, it is executed
#
# Because of this operation, actions wanting to use the value of the
# current input terminal are placed *before* the token itself. This is
# guaranteed to work as the only way to get to the production is if
# the input terminal is of the correct type.
#
# Actions wanting to be executed after the actions within one of the productions
# of a non-terminal are placed *after* the non-terminal. Otherwise, they would
# be executed before the actions within the non-terminal production due to the
# order of tokens pulled from the stack.
#
# The syntax is pretty simple, and is designed to mirror the usual
# yacc syntax.
#
# Actions are any sequence of characters enclosed in
# @. Use two @ signs to include an actual @ in the action.
#
# What I'd like to figure out is how to automate the management
# of the value stack so that actions can associate values
# with the non-terminal associated with the production in which
# they occur. This would make them work more like yacc actions as
# values could then be synthesized upwards in the grammar
#
# Perhaps a special token could be placed on the stack at the end of
# each sequence of tokens that replace a non-terminal, and this token
# could signal suitable value stack handling? That would need to know
# the number of elements that had been in the production when it was
# placed on the parse stack to know how many values to remove from the
# value stack, it would then drop that number of elements from the
# value stack and push the value computed by the last action within
# the production
#

# A calculator session is a sequence of lines

start	: line start
	|
	;


# A line is an expression followed by a newline, or just a newline
# alone.
#
# The C code implementing the calculator provides a numeric stack with
# push/pop functions. Note that this set of actions is responsible for
# maintaining that stack correctly; errors will terminate the parser, and so
# the stack could be re-initialized when the parser is restarted.
#

line	: expr NL
		@{
			printf("%g\n", pop());
		}@ 
	| NL
	;

# Three levels of precedence, (+ -), (* /) and then unary
# minus/parenthesized exprs

expr	: term expr-p
	;
expr-p	: PLUS term
		@{
			double b = pop();
			double a = pop();
			push(a + b);
		}@
	  expr-p
	| MINUS term
		@{
			double b = pop();
			double a = pop();
			push(a - b);
		}@
	  expr-p
	|
	;
term	: fact term-p
	;
term-p	: TIMES fact
		@{
			double b = pop();
			double a = pop();
			push(a * b);
		}@
	  term-p
	| DIVIDE fact
		@{
			double b = pop();
			double a = pop();
			push(a / b);
		}@
	  term-p
	|
	;
fact	: OP expr CP
	| MINUS fact
		@{
			double a = pop();
			push(-a);
		}@
	| NUMBER
		@{
			push(lex_value);
		}@
	;
