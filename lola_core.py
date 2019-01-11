#!/usr/bin/python3

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
    return item[0].islower()

def is_terminal(item):
    return item[0].isupper()

def is_action(item):
    return item[0] == '@'

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
    global first_list
    first_dictionary = {}
    first_list = ()

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
    for non_terminal in grammar:
        non_terminals += (non_terminal,)
    return non_terminals

def get_terminals(grammar):
    terminals = ("END",)
    for non_terminal, prods in grammar.items():
        for prod in prods:
            for token in prod:
                if is_terminal(token) and not token in terminals:
                    terminals += (token,)
    return terminals

def get_actions(grammar):
    actions = ()
    for non_terminal, prods in grammar.items():
        for prod in prods:
            for token in prod:
                if is_action(token) and not token in actions:
                    actions += (token,)
    return actions

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

def dump_grammar(grammar):
    for non_term, prods in grammar.items():
        print("%-20.20s" % non_term, end='')
        first=True
        for prod in prods:
            if first:
                print(":", end='')
                first = False
            else:
                print("                    |", end='')
            for token in prod:
                print(" %s" % token, end='')
            print("")
        print("                    ;")
