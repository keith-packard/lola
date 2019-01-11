#!/usr/bin/python

from lola_core import *

lex_c = False

def getc():
    global lex_c
    if lex_c:
        c = lex_c
        lex_c = False
    else:
        c = sys.stdin.read(1)
    return c

def ungetc(c):
    global lex_c
    lex_c = c

lex_value = False

def lex():
    global lex_value
    while True:
        c = getc()
        if c == '':
            return 'END'
        if c == '+':
            return "PLUS"
        if c == '-':
            return "MINUS"
        if c == '*':
            return "TIMES"
        if c == '/':
            return "DIVIDE"
        if c == '(':
            return "OP"
        if c == ')':
            return "CP"
        if c == '\n':
            return "NL"
        if '0' <= c and c <= '9':
            v = ord(c) - ord('0')
            while True:
                c = getc()
                if '0' <= c and c <= '9':
                    v = v * 10 + ord(c) - ord('0')
                else:
                    ungetc(c)
                    break;
            lex_value = v
            return "NUMBER"

value_stack = ()

def push(v):
    global value_stack
    print("\tpush %r" % v)
    value_stack = (v,) + value_stack

def pop():
    global value_stack
    v = head(value_stack)
    value_stack = rest(value_stack)
    print("\tpop %r" % v)
    return v

#
# lines : line lines
#       |
#
# expr  : term PLUS expr
#       | term MINUS expr
#       | term
#
# expr  : term expr-p
# expr-p: PLUS expr
#       | MINUS expr
#       |

grammar = {
    "start"     : (("line", "start"),
                   ()
                   ),
    "line"      : (("expr", "@PRINT", "NL"),
                   ("NL",),
                   ),
    "expr"	: (("term", "expr-p"),
    ),
    "expr-p"	: (("PLUS", "term", "@ADD", "expr-p"),
                   ("MINUS", "term", "@SUBTRACT", "expr-p"),
                   (),
    ),
    "term"	: (("fact", "term-p"),
                   ),
    "term-p"	: (("TIMES", "fact", "@TIMES", "term-p"),
                   ("DIVIDE", "fact", "@DIVIDE", "term-p"),
                   (),
                   ),
    "fact"	: (("OP", "expr", "CP"),
                   ("MINUS", "fact", "@NEGATE"),
                   ("@PUSH", "NUMBER"),
                   )
    }

def test():
    global lex_value
    global value_stack
    table = ll(grammar)
    dump_table(table)
    stack = (start_symbol,)
    token = False
    while True:
        if not token:
            token = lex()
            print("read %r" % token)

        print("\ttoken %r stack %r" % (token, stack))

        if not stack:
            if token == end_token:
                print("parse complete")
                return
            error("parse stack empty at %r" % token)

        top = head(stack)

        if is_action(top):
            print("action %r" % top)
            if top == "@PUSH":
                push(lex_value)
            elif top == "@ADD":
                push(pop() + pop())
            elif top == "@SUBTRACT":
                a = pop()
                b = pop()
                push(b - a)
            elif top == "@TIMES":
                push(pop() * pop())
            elif top == "@DIVIDE":
                a = pop()
                b = pop()
                push(b / a)
            elif top == "@NEGATE":
                a = pop()
                push(-a)
            elif top == "@PRINT":
                print("= %r" % pop())
            stack = rest(stack)
        elif is_terminal(top):
            if top == token:
                print("\tmatch %r" % token)
                stack = rest(stack)
                token = False
            else:
                error("parse error. got %r expected %r" % (token, top))
        else:
            key = (token, head(stack))
            if key not in table:
                error("parse error at %r %r" % (token, head(stack)))
            stack = table[key] + rest(stack)
        
test()
