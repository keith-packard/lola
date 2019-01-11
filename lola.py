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

from lola_core import *

import sys

grammar = {
    start_symbol: (("non-term", start_symbol),
                   ()
                   ),
    "non-term"  : (("@NONTERM", "SYMBOL", "COLON", "rules", "@RULES", "SEMI"),
                   ),
    "rules"     : (("rule", "rules-p"),
                   ),
    "rules-p"   : (("VBAR", "rule", "rules-p"),
                   (),
                   ),
    "rule"      : (("symbols", "@RULE"),
                   ),
    "symbols"   : (("@SYMBOL", "SYMBOL", "symbols"),
                   (),
                   ),
    }

lex_c = False

lex_file = sys.stdin

lex_line = 1

def onec():
    global lex_line
    global lex_file
    c = lex_file.read(1)
    if c == '\n':
        lex_line = lex_line + 1
    return c

def getc():
    global lex_c
    if lex_c:
        c = lex_c
        lex_c = False
    else:
        c = onec()
        if c == '#':
            while c != '\n':
                c = onec()
    return c

def ungetc(c):
    global lex_c
    lex_c = c

lex_value = False

def is_symbol_start(c):
    return c.isalpha() or c == '_' or c == '-'

def is_symbol_cont(c):
    return is_symbol_start(c) or c.isdigit()

def lex():
    global lex_value
    lex_value = False
    while True:
        c = getc()
        if c == '':
            return 'END'
        if c == '|':
            return "VBAR"
        if c == ':':
            return "COLON"
        if c == ';':
            return "SEMI"
        if c == '@':
            v = c
            at_line = lex_line
            while True:
                c = getc()
                if c == '':
                    error("Missing @, token started at line %d" % at_line)
                elif c == '@':
                    c = getc()
                    if c != '@':
                        ungetc(c)
                        break
                v += c
            lex_value = v
            return "SYMBOL"
        if is_symbol_start(c):
            v = c
            while True:
                c = getc()
                if is_symbol_cont(c):
                    v += c
                else:
                    ungetc(c)
                    break;
            lex_value = v
            return "SYMBOL"

def lola():
    global lex_value
    global value_stack

    # Construct the parser for lola input files
    table = ll(grammar)

    # Run the lola parser

    stack = (start_symbol,)
    token = False
    result = {}
    non_term = False
    prod = ()
    prods = ()
    while True:
        if not token:
            token = lex()

        if not stack:
            if token == end_token:
                return result
            error("parse stack empty at %r" % token)

        top = head(stack)

        if is_action(top):
            stack = rest(stack)
            if top == "@NONTERM":
                non_term = lex_value
            elif top == "@RULES":
                result[non_term] = prods
                prods = ()
                non_term = False
            elif top == "@RULE":
                prods = prods + (prod,)
                prod = ()
            elif top == "@SYMBOL":
                prod = prod + (lex_value,)
        elif is_terminal(top):
            if top == token:
                stack = rest(stack)
                token = False
            else:
                error("%d: parse error. got %r expected %r" % (lex_line, token, top))
        else:
            key = (token, head(stack))
            if key not in table:
                error("%d: parse error at %r %r" % (lex_line, token, head(stack)))
            stack = table[key] + rest(stack)
        
def to_c(string):
    return string.replace("-", "_")

def action_has_name(action):
    return action[1].isalpha()

def action_name(token_values, action):
    if action_has_name(action):
        action = to_c(action)[1:]
        end = action.find(' ')
        if end != -1:
            action = action[0:end]
        return "ACTION_" + action
    else:
        return "ACTION_%d" % token_values[action]

def action_value(action):
    if action_has_name(action):
        end = action.find(' ')
        if end == -1:
            return ""
    else:
        end = 0
    return action[end+1:]

def terminal_name(terminal):
    return to_c(terminal)

def non_terminal_name(non_terminal):
    return "NON_TERMINAL_" + to_c(non_terminal)

def token_name(token_values, token):
    if is_action(token):
        return action_name(token_values, token)
    elif is_terminal(token):
        return terminal_name(token)
    else:
        return non_terminal_name(token)

def dump_c(grammar, parse_table):
    terminals = get_terminals(grammar)
    num_terminals = len(terminals)
    non_terminals = get_non_terminals(grammar)
    num_non_terminals = len(non_terminals)
    actions = get_actions(grammar)
    num_actions = len(actions)
    print("/* %d terminals %d non_terminals %d actions */" % (num_terminals, num_non_terminals, num_actions))
    print("")
    print("#if !defined(GRAMMAR_TABLE) && !defined(ACTIONS_SWITCH) && !defined(TOKEN_NAMES)")
    print("typedef enum {")
    print("    TOKEN_NONE = 0,")
    token_value = {}
    value = 1
    for terminal in terminals:
        token_value[terminal] = value
        print("    %s = %d," % (terminal_name(terminal), value))
        value += 1
    print("    FIRST_NON_TERMINAL = %d," % value)
    for non_terminal in non_terminals:
        token_value[non_terminal] = value
        print("    %s = %d," % (non_terminal_name(non_terminal), value))
        value += 1
    print("    FIRST_ACTION = %d," % value)
    for action in actions:
        token_value[action] = value
        print("    %s = %d," % (action_name(token_value, action), value))
        value += 1
    print("} __attribute__((packed)) token_t;")
    print("#endif /* !GRAMMAR_TABLE && !ACTIONS_SWITCH */")
    print("")
    print("#ifdef GRAMMAR_TABLE")
    print("#undef GRAMMAR_TABLE")
    print("static const token_t parse_table[] = {")
    for terminal in terminals:
        for non_terminal in non_terminals:
            key = (terminal, non_terminal)
            if key in parse_table:
                prod = parse_table[key]
                print("    %s, %s, " % (terminal_name(terminal), non_terminal_name(non_terminal)), end='')
                for token in prod:
                    print("%s, " % token_name(token_value, token), end='')
                print("TOKEN_NONE,")
    print("};")
    print("#endif /* GRAMMAR_TABLE */")
    print("")
    print("#ifdef ACTIONS_SWITCH")
    print("#undef ACTIONS_SWITCH")
    for action in actions:
        print("    case %s:" % action_name(token_value, action))
        print("        %s; break;" % action_value(action))
    print("#endif /* ACTIONS_SWITCH */")
    print("#ifdef TOKEN_NAMES")
    print("#undef TOKEN_NAMES")
    print("static const char *const token_names[] = {")
    print('0,');
    for terminal in terminals:
        print('"%s",' % (terminal))
    for non_terminal in non_terminals:
        print('"%s",' % (non_terminal))
    for action in actions:
        print('"%s",' % (action_name(token_value, action)))
    print("};")
    print("#endif /* TOKEN_NAMES */")

def main():
    grammar = lola()
    parse_table = ll(grammar)
    print("#ifdef COMMENT")
    dump_grammar(grammar)
    dump_table(parse_table)
    print("#endif /* COMMENT */")
    dump_c(grammar, parse_table)

main()
