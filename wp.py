#!/usr/bin/python

import sys
from pycparser import c_parser, c_ast, parse_file
import ast2str, str2py
import constraint

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

def solve_no_branch_postcond(assign_list, end_cond, affected_vars):
    if len(assign_list) == 0:
        end_cond[0].show()        
        return end_cond
    else:
        assign_list.reverse()
        assign_list_str = [ast2str.assign(a) for a in assign_list]
        solve(assign_list_str, end_cond, affected_vars)
        return end_cond #wrong, must propagate conditions
        
def solve(assign_list_str, end_cond, affected_vars):
    print "solving"
    problem = constraint.Problem()
    print affected_vars
    for var in affected_vars:
        problem.addVariable(var, range(1000))
        
    for a in assign_list_str:
        print a
        
    f_body = assign_list_str
    f_body.append("return %s and \\" % ast2str.cond(end_cond[0]))
    for cond in end_cond[1:]:
        c_s = ast2str.cond(cond)
        print c_s
    f_body.append("True")

    
    print "here"
    print f_body
    print "done"
    av_list = list(affected_vars)
    argsstr = ', '.join([a for a in av_list])
    print argsstr, av_list
    
    cons_f = str2py.function(argsstr, assign_list_str)
    problem.addConstraint(cons_f, av_list)
    print cons_f(0, 1)
    print problem.getSolution()
