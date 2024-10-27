#!/usr/bin/env python3
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
    if lex_c is not False:
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
        if c == '{':
            return "OC"
        if c == '}':
            return "CC"
        if c == ',':
            return "COMMA"
        if c == ':':
            return "COLON"
        if c == '[':
            return "OS"
        if c == ']':
            return "CS"
        if c == '\n' or c == ' ' or c == '\t':
            continue
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
        if c == '"':
            v = ''
            while True:
                c = getc()
                if c == '"':
                    break
                if c == '\\':
                    c = getc()
                    if c == 'b':
                        c = '\b'
                    elif c == 'f':
                        c = '\f'
                    elif c == 'n':
                        c = '\n'
                    elif c == 'r':
                        c = '\r'
                    elif c == 't':
                        c = '\t'
                v += c
            lex_value = v
            return "STRING"
        v = c
        if 'a' <= c and c <= 'z':
            while True:
                c = getc()
                if 'a' <= c and c <= 'z':
                    v = v + c
                else:
                    ungetc(c)
                    break;
            if v == 'true':
                return "TRUE"
            if v == 'false':
                return "FALSE"
            if v == 'null':
                return "NULL"
        print('Invalid token %s. Skipped' % v)
            

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

from pyjson_gram import *

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
            if top == "@VALUE":
                print("%r\n" % pop())
                break
            elif top == "@OBJSTART":
                push({})
            elif top == "@OBJEND":
                pass
            elif top == "@NAME":
                push(lex_value)
            elif top == "@MEMBER":
                value = pop()
                name = pop()
                obj = pop()
                obj[name] = value
                push(obj)
            elif top == "@ARRSTART":
                push([])
            elif top == "@ARREND":
                pass
            elif top == "@ARRADD":
                value = pop()
                arr = pop()
                arr.append(value)
                push(arr)
            elif top == "@STRING" or top == "@NUMBER":
                push(lex_value)
            elif top == "@TRUE":
                push(True)
            elif top == "@FALSE":
                push(False)
            elif top == "@NULL":
                push(None)
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
