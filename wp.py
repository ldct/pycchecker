#!/usr/bin/python

import sys
from pycparser import c_parser, c_ast, parse_file

parser = c_parser.CParser()

s = """
int foo() {
int a,b;
a=b+3;
b=(a^2)+2*(a*b)+(b/a);
return 1;
}
"""

parser = c_parser.CParser()
ast = parser.parse(s)

#ast.show()

def solve_no_branch_postcond(assign_list, end_cond):
    if len(assign_list) == 0:
        return end_cond
    else:
        print "not implemented yet"
        return 42
