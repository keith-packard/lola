#!/usr/bin/python3
import sys

debug_indent = 0

def debug_in():
    global debug_indent
    debug_indent += 1

def debug_out():
    global debug_indent
    debug_indent -= 1

show_debug = True

def debug(s):
    global debug_indent, show_debug
    if show_debug:
        print("    " * debug_indent, end='')
        print(s)

calc_lex_c = False

def calc_getc():
    global calc_lex_c
    if calc_lex_c:
        c = calc_lex_c
        calc_lex_c = False
    else:
        c = sys.stdin.read(1)
    return c

def calc_ungetc(c):
    global calc_lex_c
    calc_lex_c = c

calc_lex_value = False

def calc_lex():
    while True:
        c = calc_getc()
        if c == '':
            sys.exit(0)
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
            return "END"
        if '0' <= c and c <= '9':
            v = ord(c) - ord('0')
            while True:
                c = calc_getc()
                if '0' <= c and c <= '9':
                    v = v * 10 + ord(c) - ord('0')
                else:
                    calc_ungetc(c)
                    break;
            return ("NUMBER", v)

def parse(table, lex, action):
    stack = []
    value_stack = []

    a = lex()
    lex_value = None
    if type(a) is tuple:
        lex_value = a[1]
        a = a[0]
    while True:
        debug("\t\t%-10.10s %r %r" % (a, stack, value_stack))
        if not stack:
            s = 0
        else:
            s = stack[-1]
        if a not in table[s]:
            print("Syntax error")
            return False
        act = table[s][a]
        debug("\taction %r" % (act,))
        if act[0] == 'shift':
            debug("shift %d" % act[1])
            stack.append(act[1])
            value_stack.append(lex_value)
            a = lex()
            lex_value = None
            if type(a) is tuple:
                lex_value = a[1]
                a = a[0]
        elif act[0] == 'reduce':
            debug("reduce %s %d %d" % (act[1], act[2], act[3]))
            non_terminal = act[1]
            action_values = []
            for b in range(act[3]):
                stack.pop()
                action_values = [value_stack.pop()] + action_values
            value_stack.append(action(act[2], action_values))
            if not stack:
                t = 0
            else:
                t = stack[-1]
            debug("\tgoto (%r, %r) → %d" % (t, non_terminal, table[t][non_terminal]))
            stack.append(table[t][non_terminal])
        elif act[0] == 'accept':
            return (action(0, [value_stack.pop()]))
    return True

exec(open('calc-slr-bits.py').read())

while True:
    parse(table, calc_lex, action)
