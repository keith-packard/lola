#!/usr/bin/python3
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

import sys

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

def head(s):
    return s[0]

def rest(s):
    return s[1:]

def push(v):
    global value_stack
    value_stack = (v,) + value_stack

def pop():
    global value_stack
    v = head(value_stack)
    value_stack = rest(value_stack)
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

from lola_test_gram import *

def is_non_terminal(item):
    return item[0].islower()

def is_terminal(item):
    return item[0].isupper()

def is_action(item):
    return item[0] == '@'

def error(msg):
    print(msg)
    exit(1)

def test():
    global lex_value
    global value_stack
    global parse_table
    table = parse_table
    stack = ('start',)
    token = False
    while True:
        if stack:
            top = head(stack)
            stack = rest(stack)
        else:
            top = False

        if top and is_action(top):
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
            continue

        if not token:
            token = lex()

        if not top:
            if token == 'END':
                return
            error("parse stack empty at %r" % token)

        if is_terminal(top):
            if top == token:
                token = False
            else:
                error("parse error. got %r expected %r" % (token, top))
        else:
            key = (token, top)
            if key not in table:
                error("parse error at %r %r" % (token, top))
            stack = table[key] + stack
        
test()
