#!/usr/bin/python3

import sys

# ll parser table generator
#
# the format of the grammar is:
#
# {"non-terminal": (("SYMBOL", "non-terminal", "#action"), (production), (production)),
#  "non-terminal": ((production), (production), (production)),
#  }
#
# The start symbol must be named "start"
#

end_token="END$"

def productions(grammar, non_terminal):
    return grammar[non_terminal]

# data abstraction
#
# a non terminal is a string starting with lower case
# a terminal is a string starting with upper case
# an action is a string starting with '#'
#

def is_non_terminal(item):
    return item[0].islower()

def is_terminal(item):
    return item[0].isupper()

def is_action(item):
    return item[0] == '#'

def is_null_production(p):
    if len(p) == 0:
        return True
    elif is_action(p[0]):
        return is_null_production(p[1:])
    else:
        return False

start_symbol = "start"

def is_start_symbol(item):
    global start_symbol
    return item == start_symbol

def head(list):
    return list[0]

def rest(list):
    return list[1:]

def error(msg):
    print(msg)
    exit(1)

#
# generate the first set for a collection of productions
#  this is used to generate the first set for a particular
#  non-terminal usually
#
def first_set(grammar, prods):
    if len(prods) == 0:
        return ()
    elif is_null_production(head(prods)):
        return ((),) + first_set(grammar, rest(prods))
    else:
        return first(grammar, head(prods)) + first_set(grammar, rest(prods))

first_list = ()

def unique(list):
    if not list:
        return list
    f = head(list)
    r = rest(list)
    if f in r:
        return unique(r)
    else:
        return (f,) + unique(r)

def delete(elt, list):
    ret = ()
    for i in list:
        if i != elt:
            ret = ret + (i,)
    return ret

#
# generate the first set for a single symbol This is easy for a
#  terminal -- the result is the item itself.  For non-terminals, the
#  first set is the union of the first sets of all the productions
#  that derive the non-terminal
#
# Note that this also checks to see if the grammar is left-recursive.
# This will succeed because a left recursive grammar will always
# re-reference a particular non-terminal when trying to generate a
# first set containing it.
#

def first_for_symbol(grammar, item):
    global first_list
    if item in first_list:
        error("lola: left-recursive grammar for symbol %s" % item)
    first_list = (item,) + first_list
    ret = False
    if is_terminal(item):
        ret = (item,)
    elif is_non_terminal(item):
        ret = unique(first_set(grammar, productions(grammar, item)))
    first_list = rest(first_list)
    return ret

#
# generate the first list for a production.
#
# the first list is the set of symbols which are legal
# as the first symbols in some possible expansion of the
# production.  The cases are simple:
#
# if the (car production) is a terminal, then obviously
# the only possible first symbol is that terminal
#
# Otherwise, generate the first lists for *all* expansions
# of the non-terminal (car production).  If that list doesn't
# contain an epsilon production 'nil, the we're done.  Otherwise,
# this set must be added to the first set of (cdr production) because
# some of the possible expansions of the production will not have any
# terminals at all from (car production).
#
# Note the crufty use of dictionaries to save old expansion of first
# sets.  This is because both ll and follow call first quite often,
# frequently for the same production
#

first_dictionary = {}

def reset_first():
    global first_dictionary
    first_dictionary = {}

def first(grammar, production):
    global first_dictionary
    while production and is_action(head(production)):
        production = rest(production)
    if production in first_dictionary:
        ret = first_dictionary[production]
    else:
        if production:
            ret = first_for_symbol(grammar, head(production))
            if () in ret:
                ret = delete((), ret) + first(grammar, rest(production))
        else:
            ret = ((),)
        first_dictionary[production] = ret
    return ret

def member(item, list):
    if item in list:
        return list[list.index(item):]
    else:
        return ()

#
# generate the follow set of a for an item in a particular
# production which derives a particular non-terminal.
#
# This is nil if the production does
# not contain the item.
#
# Otherwise, it is the first set for the portion of the production
# which follows the item -- if that first set contains nil, then the
# follow set also contains the follow set for the non-terminal which
# is derived by the production
#

def follow_in_production(grammar, item, non_terminal, production, non_terminals):
    r = member(item, production)
    if not r:
        return ()
    f = first(grammar, rest(r))
    if () in f:
        f = delete((), f) + follow(grammar, non_terminal, non_terminals)
    return f

#
# loop through the productions of a non-terminal adding
# the follow sets for each one.  Note that this will often
# generate duplicate entries -- as possibly many of the
# follow sets for productions will contain the entire follow
# set for the non-terminal
#

def follow_in_non_terminal (grammar, item, non_terminal, non_terminals):
    ret = ()
    for prod in productions(grammar, non_terminal):
        ret += follow_in_production(grammar, item, non_terminal, prod, non_terminals)
    return ret

#
# generate the follow set for a particular non-terminal
# The only special case is for the
# start symbol who's follow set also contains the
# end-token
#

follow_dictionary = {}

def reset_follow():
    global follow_dictionary
    follow_dictionary = {}

def follow(grammar, item, non_terminals):
    global follow_dictionary
    if item in follow_dictionary:
        ret = follow_dictionary[item]
    else:
        ret = ()
        for non_terminal in non_terminals:
            if non_terminal != item:
                ret += follow_in_non_terminal(grammar, item, non_terminal, non_terminals)

        if is_start_symbol(item):
            ret = (end_token,) + ret

        ret = unique(ret)
        follow_dictionary[item] = ret

    return ret

#
# this makes an entry in the output list, this is just one
# of many possible formats
#

def make_entry(terminal, non_terminal, production):
    return {(terminal, non_terminal): production}

def add_dict(a,b):
    for key,value in b.items():
        a[key] = value

#
# generate the table entries for a particular production
# this is taken directly from Aho, Ullman and Seti
#
# Note: this function uses dynamic scoping -- both non-terminal
# and non-terminals are expected to have been set by the caller
#

def ll_one_production(grammar, production, non_terminal, non_terminals):
    firsts = first(grammar, production)
    ret = {}
    for f in firsts:
        if not f:
            follows = follow(grammar, non_terminal, non_terminals)
            for f in follows:
                add_dict(ret, make_entry(f, non_terminal, production))
        elif is_terminal(f):
            add_dict(ret, make_entry(f, non_terminal, production))
    return ret

#
# generate the table entries for all productions of
# a particular non-terminal
#
def ll_one_non_terminal(grammar, non_terminal, prods, non_terminals):
    ret = {}
    for p in prods:
        add_dict(ret, ll_one_production(grammar, p, non_terminal, non_terminals))
    return ret

#
# generate the table entries for all the non-terminals
#

def ll_non_terminals(grammar, non_terminals):
    ret = {}
    for non_terminal in non_terminals:
        add_dict(ret, ll_one_non_terminal(grammar, non_terminal, productions(grammar, non_terminal), non_terminals))
    return ret

def get_non_terminals(grammar):
    non_terminals = ()
    for e in grammar:
        non_terminals += (e,)
    return non_terminals

#
# produce a parse table for the given grammar
#

def ll (grammar):
    reset_first()
    reset_follow()
    non_terminals = get_non_terminals(grammar)
    return ll_non_terminals(grammar, non_terminals)


def dump_table(table):
    print("Parse table")
    for key,value in table.items():
        print("\t%r -> %r" % (key, value))

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
            return 'END$'
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

input = ("NUMBER", "PLUS", "NUMBER", "TIMES", "NUMBER", "END$")

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
    "line"      : (("expr", "#PRINT", "NL"),
                   ("NL",),
                   ),
    "expr"	: (("term", "expr-p"),
    ),
    "expr-p"	: (("PLUS", "term", "#ADD", "expr-p"),
                   ("MINUS", "term", "#SUBTRACT", "expr-p"),
                   (),
    ),
    "term"	: (("fact", "term-p"),
                   ),
    "term-p"	: (("TIMES", "fact", "#TIMES", "term-p"),
                   ("DIVIDE", "fact", "#DIVIDE", "term-p"),
                   (),
                   ),
    "fact"	: (("OP", "expr", "CP"),
                   ("MINUS", "fact", "#NEGATE"),
                   ("#PUSH", "NUMBER"),
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
            if top == "#PUSH":
                push(lex_value)
            elif top == "#ADD":
                push(pop() + pop())
            elif top == "#SUBTRACT":
                a = pop()
                b = pop()
                push(b - a)
            elif top == "#TIMES":
                push(pop() * pop())
            elif top == "#DIVIDE":
                a = pop()
                b = pop()
                push(b / a)
            elif top == '#NEGATE':
                a = pop()
                push(-a)
            elif top == "#PRINT":
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
