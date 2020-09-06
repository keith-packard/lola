#!/usr/bin/python3
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
                c = getc()
                if '0' <= c and c <= '9':
                    v = v * 10 + ord(c) - ord('0')
                else:
                    ungetc(c)
                    break;
            lex_value = v
            return "NUMBER"

def dump_grammar(grammar, file=sys.stdout):
    prev_non_term = False
    for p in range(len(grammar)):
        prod = grammar[p]
        non_term = prod[0]
        if non_term != prev_non_term:
            if prev_non_term:
                print("%s ;" % (' ' * 20,), file=file)
            print("%2d: %-16.16s : " % (p, non_term), end='', file=file)
            prev_non_term = non_term
        else:
            print("%2d: %s | " % (p, " " * 16,), end='', file=file)
        for token in prod[1:]:
            print(" %s" % token, end='', file=file)
        print("", file=file)
    if prev_non_term:
        print("%s ;" % (" " * 20,), file=file)

end_token="END"

def productions(grammar, non_terminal):
    if non_terminal not in grammar:
        error("Undefined non-terminal %s" % non_terminal)
    return grammar[non_terminal]

# data abstraction
#
# a non terminal is a string starting with lower case
# a terminal is a string starting with upper case
# an action is a string starting with '@'
#

def is_non_terminal(item):
    return item is not None and item[0].islower()

def is_terminal(item):
    return item is not None and item[0].isupper()

def is_action(item):
    return item[0] == '@'

def is_null_production(prod):
    ret = True
    for p in range(1,len(prod)):
        if not is_action(prod[p]):
            ret = False
    return ret

start_symbol = "start"

def is_start_symbol(item):
    global start_symbol
    return item == start_symbol

def fprint(msg, end='\n', file=sys.stdout):
    file.write(msg)
    file.write(end)

def error(msg):
    fprint(msg, file=sys.stderr)
    exit(1)

#
# generate the first set for the productions
#  of a non-terminal
#
def first_set(grammar, non_terminal):
    ret=[]
    for prod in grammar:
        if prod[0] == non_terminal:
            if is_null_production(prod):
                ret.append(())
            else:
                ret += first(grammar, prod)
    return ret

def unique(list):
    ret = []
    for l in list:
        if l not in ret:
            ret.append(l)
    return ret

def delete(elt, list):
    ret = []
    for i in list:
        if i != elt:
            ret.append(i)
    return ret

#
# generate the first set for a single symbol This is easy for a
#  terminal -- the result is the item itself.  For non-terminals, the
#  first set is the union of the first sets of all the productions
#  that derive the non-terminal
#

def first_for_symbol(grammar, symbol):

    ret = False
    if is_terminal(symbol):
        ret = [symbol,]
    elif is_non_terminal(symbol):
        set = first_set(grammar, symbol)
        print("first set for %s is %r" % (symbol, set))
        ret = unique(set)

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
    global first_list
    first_dictionary = {}
    first_list = ()

debug_indent = 0

def debug_in():
    global debug_indent
    debug_indent += 1

def debug_out():
    global debug_indent
    debug_indent -= 1

def debug(s):
    global debug_indent
    print("    " * debug_indent, end='')
    print(s)

def first(grammar, production):
    global first_dictionary

    debug_in()
    while production and is_action(production[0]):
        production = production[1:]

    if production in first_dictionary:
        ret = first_dictionary[production]
    else:
        debug("Compute first for production %r" % (production,))
        if production:
            ret = first_for_symbol(grammar, production[0])
            if () in ret:
                ret = delete((), ret) + first(grammar, production[1:])
        else:
            ret = [()]
        debug("first is %r" % (ret,))
        first_dictionary[production] = ret

    debug_out()
    return ret

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

def follow_in_production(grammar, production, non_terminal):

    # Find all instances of the non_terminal in this production; it
    # may be repeated

    f = []
    debug_in()
    debug("compute follow_in_production %r %s" % (production, non_terminal))
    for i in range(1,len(production)):
        if production[i] == non_terminal:
            rest = production[i+1:]
            more = first(grammar, rest)
            debug("first for %r is %r" % (rest, more))
            f += more

    if () in f:
        debug("adding follow for %r" % production[0])
        f = delete((), f) + follow(grammar, production[0])
    debug("follow_in_production %r" % (f,))
    debug_out()
    return f

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

#
# A list of in-process follow calls
# Use this to avoid recursing into the same
# non-terminal
#
follow_stack = []

def follow(grammar, non_terminal):
    global follow_dictionary, follow_stack

    debug_in()
    debug("compute follow for %s" % non_terminal)
    if non_terminal in follow_dictionary:
        ret = follow_dictionary[non_terminal]
    elif non_terminal in follow_stack:
        debug("follow recurse on %s" % (non_terminal,))
        ret = []
    else:
        ret = []
        follow_stack.append(non_terminal)
        for prod in grammar:
            if non_terminal in prod[1:]:
                ret += follow_in_production(grammar, prod, non_terminal)
        follow_stack.pop()

        if is_start_symbol(non_terminal):
            ret.append(end_token)

        ret = unique(ret)
        follow_dictionary[non_terminal] = ret

    debug("follow for %s is %r" % (non_terminal, ret))
    debug_out()
    return ret


grammar = (
# 0
    ("start", "e",),
# 1
    ("e", "e", "PLUS", "t",),
# 2
    ("e", "t",),
# 3
    ("t", "t", "TIMES", "f",),
# 4
    ("t", "f",),
# 5
    ("f", "OP", "e", "CP",),
# 6
    ("f", "NUMBER",),
    )


value_stack = []

def action(production):
    if production == 6:
        value_stack.append(lex_value)
    elif production == 3:
        a = value_stack.pop()
        b = value_stack.pop()
        value_stack.append(b * a)
    elif production == 1:
        a = value_stack.pop()
        b = value_stack.pop()
        value_stack.append(b + a)
    elif production == 0:
        a = value_stack.pop()
        print("Value: %r" % (a,))

def parse(table):
    a = lex()
    stack = [0]
    while True:
        print("\t\t%-10.10s %r" % (a, stack))
        s = stack[-1]
        act = table[s][a]
#        print("\taction %r" % (act,))
        if act[0] == 'shift':
            stack.append(act[1])
            a = lex()
        elif act[0] == 'reduce':
            production = grammar[act[1]]
            action(act[1])
            non_terminal = production[0]
            handle = production[1:];
            print("%-5.5s -> %s" % (non_terminal, handle))
            for b in handle:
                stack.pop()
            t = stack[-1]
            stack.append(table[t][non_terminal])
        elif act[0] == 'accept':
            action(0)
            break
        else:
            print("syntax error")
            break
    return True

def closure(grammar, I):
    # Initially, add every item in I to the closure
    C = I[:]

    while True:
        added = False
        # Find something to add to the closure
        for i in C:
            prod_no = i[0]
            pos = i[1]

            # If the element at the item location is a non-terminal,
            # then add all productions at position 0 to the closure
            prod = grammar[prod_no]
            if pos + 1 < len(prod):
                symbol = prod[pos+1]
                if is_non_terminal(symbol):
                    for p in range(len(grammar)):
                        if grammar[p][0] == symbol:
                            item = (p, 0)
                            if item not in C:
                                C.append(item)
                                added = True
        if not added:
            break
    return C

def goto(grammar, I, X):
    # Closure of the set of all items
    # [A → αX·β] such that [A → α·Xβ] is in I
    items = []
    for p in range(len(grammar)):
        prod = grammar[p]
        if X in prod[1:]:
            for i, sym in enumerate(prod[1:]):
                if sym == X:
                    item = (p, i)
                    if item in I:
                        items.append((p, i+1))
    return closure(grammar, items)

def symbols(grammar):
    symbols = []
    for prod in grammar:
        for symbol in prod:
            if symbol not in symbols:
                symbols.append(symbol)
    return symbols

def dump_item(grammar, item):
    prod = grammar[item[0]]
    pos = item[1]
    print("    %-10.10s :" % (prod[0],), end='')
    for p in range(len(prod)):
        if p == pos:
            print(" ·", end='')
        if p + 1 < len(prod):
            print(" %s" % (prod[p+1],), end='')
    print("")

def dump_items(grammar, items):
    for i in items:
        dump_item(grammar, i)

def dump_states(grammar, states):
    for s in range(len(states)):
        print("State %d" % s)
        dump_items(grammar, states[s])

def items(grammar):
    C = [closure(grammar, [(0, 0),])]
    S = symbols(grammar)
    while True:
        added = False
        for I in C:
            for s in S:
                G = goto(grammar, I, s)
                if G and G not in C:
                    C.append(G)
                    add = True
        if not added:
            break
    return C

table = (
# 0
    {
        "NUMBER": ('shift', 5),
        "OP"    : ('shift', 4),
        "e"     : 1,
        "t"     : 2,
        "f"     : 3
    },
# 1
    {
        "PLUS"  : ('shift', 6),
        "END"   : ('accept',),
    },
# 2
    {
        "PLUS"  : ('reduce', 2),
        "TIMES" : ('shift', 7),
        "CP"    : ('reduce', 2),
        "END"   : ('reduce', 2),
    },
# 3
    {
        "PLUS"  : ('reduce', 4),
        "TIMES" : ('reduce', 4),
        "CP"    : ('reduce', 4),
        "END"   : ('reduce', 4),
    },
# 4
    {
        "NUMBER": ('shift', 5),
        "OP"    : ('shift', 4),
        "e"     : 8,
        "t"     : 2,
        "f"     : 3,
    },
# 5
    {
        "PLUS"  : ('reduce', 6),
        "TIMES" : ('reduce', 6),
        "CP"    : ('reduce', 6),
        "END"   : ('reduce', 6),
    },
# 6
    {
        "NUMBER": ('shift', 5),
        "OP"    : ('shift', 4),
        "t"     : 9,
        "f"     : 3,
    },
# 7
    {
        "NUMBER": ('shift', 5),
        "OP"    : ('shift', 4),
        "f"     : 10,
    },
# 8
    {
        "PLUS"  : ('shift', 6),
        "CP"    : ('shift', 11),
    },
# 9
    {
        "PLUS"  : ('reduce', 1),
        "TIMES" : ('shift', 7),
        "CP"    : ('reduce', 1),
        "END"   : ('reduce', 1),
    },
# 10
    {
        "PLUS"  : ('reduce', 3),
        "TIMES" : ('reduce', 3),
        "CP"    : ('reduce', 3),
        "END"   : ('reduce', 3),
    },
# 11
    {
        "PLUS"  : ('reduce', 5),
        "TIMES" : ('reduce', 5),
        "CP"    : ('reduce', 5),
        "END"   : ('reduce', 5),
    },
    )


def at(grammar, item):
    prod = grammar[item[0]]
    pos = item[1]
    if pos + 1 < len(prod):
        return prod[pos + 1]
    return None

def goto_state(grammar, C, state, symbol):
    G = goto(grammar, C[state], symbol)
    if not G:
        return None
    return C.index(G)

def non_terminals(grammar):
    n = []
    for prod in grammar:
        if prod[0] not in n:
            n.append(prod[0])
    return n

def terminals(grammar):
    t = []
    for prod in grammar:
        for symbol in prod[1:]:
            if is_terminal(symbol) and symbol not in t:
                t.append(symbol)
    t.append(end_token)
    return t

def print_table(grammar, T):
    nons = non_terminals(grammar)
    terms = terminals(grammar)
    for s in range(len(T)):
        print("State %d" % s)
        S = T[s]
        for t in terms:
            if t in S:
                print("     %-10.10s : %r," % (t, S[t]))
        for n in nons:
            if n in S:
                print("     %-10.10s : %r," % (n, S[n]))

def slr(grammar):
    C = items(grammar)
    print("States")
    dump_states(grammar, C)
    print("---------")
    table = []
    N = non_terminals(grammar)
    for n in N:
        follow(grammar, n)
    for c in range(len(C)):
        I = C[c]
        debug("Compute state %d (%r)" % (c, I))
        debug_in()
        actions = {}
        for i in range(len(I)):
            item = I[i]
            a = at(grammar, item)
            prod = item[0]
            pos = item[1]
            non_terminal = grammar[prod][0]
            debug("Item %r at %r non_terminal %s" % (item, a, non_terminal))
            if is_terminal(a):
                j = goto_state(grammar, C, c, a)
                if j is not None:
                    actions[a] = ('shift', j)
            elif a is None:
                if is_start_symbol(non_terminal):
                    actions[end_token] = ('accept',)
                else:
                    j = item[0]
                    f = follow(grammar, non_terminal)
                    for a in f:
                        actions[a] = ('reduce', j)
        for n in N:
            j = goto_state(grammar, C, c, n)
            if j is not None:
                actions[n] = j
        debug_out()
        debug("Actions state %d = %r" % (c, actions))
        table.append(actions)
    print_table(grammar, table)
    return table
            
dump_grammar(grammar)

new_table = slr(grammar)

while parse(new_table):
    pass
