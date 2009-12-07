#!/usr/bin/python

import sys
from pycparser import c_parser, c_ast, parse_file
from generate_traces import extract_globals, scan_statement, possible_error_traces
from expand_trace import expand_trace, expanded_trace
from solve_trace import solve_trace

parser = c_parser.CParser()
ast = parse_file('simple-flow.c', use_cpp=True)

global_vars = []

for obj in ast.ext:
    if isinstance(obj, c_ast.Decl):
        global_decl = extract_globals(obj)
        global_vars.append(global_decl)
    elif isinstance(obj, c_ast.FuncDef):
        print "\n\nscanning function '%s'" % obj.decl.name
        for stmt in obj.body.stmts:
            scan_statement(stmt, [obj] + [stmt])

print
print len(possible_error_traces), "error trace(s)"
for trace in possible_error_traces:
    #for t in trace: print t
    print
    expand_trace(trace)
    print
    #print expanded_trace
    print
    solve_trace(expanded_trace)
