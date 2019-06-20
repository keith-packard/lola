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

grammar = {
    "lines"     : (("line", "lines"),
                   ()
                   ),
    "line"      : (("expr", "#PRINT", "NL"),
                   ("NL",),
                   ),
    "expr"	: (("term", "PLUS", "expr", "#ADD"),
                   ("term", "MINUS", "expr", "#SUBTRACT"),
                   ("term",)
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

def productions(non_terminal):
    return grammar[non_terminal]

# flo
#
# factor left common expressions out of a grammar
#

def head(list):
    return list[0]

def rest(list):
    return list[1:]

def nthrest(list, n):
    return list[n:]

def error(msg):
    print(msg)
    exit(1)

#
# remove the first element from each of a list
# of productions (unless the production is nil)
#

def clip_firsts(prods):
    ret = ()
    for prod in prods:
        if prod:
            ret += (head(prod),)
    return ret

#
# return the first duplicated element from a list of elements
#

def find_common(firsts):
    while firsts:
        f = head(firsts)
        firsts = rest(firsts)
        if f in firsts:
            return f

#
# return a list of productions which have the given
# element as their first member
#
def with_first(prods, first):
    ret = ()
    for prod in prods:
        if first == head(prod):
            ret = ret + (prod,)
    return ret

#
# return a list of productions which *don't* have the given
# element as their first member
#
def without_first (prods, first):
    ret = ()
    for prod in prods:
        if first != head(prod):
            ret = ret + (prod,)
    return ret

#
# strip the first 'count' elements off a list of productions
#

def remove_firsts (prods, count):
    ret = ()
    for prod in prods:
        ret = ret + (nthrest(prod, count),)
    return ret

#
# return True if each production in the list has the same first
# element
#
def all_common_first(prods):
    while len(prods) >= 2:
        if head(prods[0]) != head(prods[1]):
            return False
        prods = rest(prods)
    return True

#
# return the maximal list of common first sub-lists
# from a set of productions
#

def max_common(prods):
    ret = ()
    while all_common_first(prods):
        ret = ret + (head(prods[0]),)
        prods = remove_firsts(prods, 1)
    return ret

#
# factor out common left sub-lists from the list
# of productions
#

def eliminate_common(non_terminal):
    prods = productions(non_terminal)
    firsts = clip_firsts(prods)
    common = find_common(firsts)
    if common:
        removed = with_first(prods, common)
        remain = without_first(prods, common)
        common_list = max_common(removed)
        new_non_terminal = non_terminal
        while True:
            new_non_terminal = new_non_terminal + "-p"
            if new_non_terminal not in grammar:
                break
        grammar[new_non_terminal] = remove_firsts(removed, len(common_list))
        grammar[non_terminal] = ((common_list + (new_non_terminal,)),) + remain
	   
#
# remove common left sub-expressions from each non-terminal
# in the grammar
#
def factor_left(non_terminals):
    for non_terminal in non_terminals:
        eliminate_common(non_terminal)

def get_non_terminals(grammar):
    non_terminals = ()
    for e in grammar:
        non_terminals += (e,)
    return non_terminals


def dump_grammar(grammar):
    for nt,prods in grammar.items():
        print("%s" % nt)
        started = False
        for prod in prods:
            label = ":"
            if started:
                label = "|"
            print("\t%s %s" % (label, prod))
            started = True
        print("\t;")

def flo():
    factor_left(get_non_terminals(grammar))

flo()

dump_grammar(grammar)
