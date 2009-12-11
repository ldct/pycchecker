#!/usr/bin/python

import sys
from constraint import *
from pycparser import c_parser, c_ast, parse_file
import expand_trace
import wp

problem = Problem()
affected_vars = set()

def add_ptr_var(name):
    affected_vars.add(name)
    problem.addVariable(name, ['null', 'non-null'])
    
def harvest_affected(assign):
    affected = []
    def _recurse(value):
        if isinstance(value, c_ast.ID):
            affected.append(value)
        elif isinstance(value, c_ast.Assignment):
            _recurse(value.rvalue)
        else:
            for child in value.children():
                _recurse(child)
    _recurse(assign)
    for a in affected:
        yield a.name

def solve_trace(trace):
    var1 = trace.end_cond[0].cond.left.name    #huh? why?
    add_ptr_var(var1)
    solve_trace_recurse(trace)

def solve_trace_recurse(trace):
    no_branch_section = []

    for element in reversed(trace):
        if isinstance(element, c_ast.Assignment):           #assignment: just add to n_b_s to pass to wp.py
            assert(isinstance(element.lvalue, c_ast.ID))
            if (element.lvalue.name in affected_vars):
                element.show()
                no_branch_section.append(element)                
                print "assignment to affected var, should harvest more"
                for affected in harvest_affected(element):
                    print affected
                    affected_vars.add(affected)
            else:
                print "useless: ", element
            trace.remove(element)
        elif isinstance(element, expand_trace.Condition):   #condition: branch point ahead.
            trace.remove(element)
            
            for affected in element.show_affected_vars():
                #affected.show()
                affected_vars.add(affected)
                
            print "-----------------"    
            end_conditions = []     #tmp
            for cond in wp.solve_no_branch_postcond(no_branch_section, trace.end_cond):
                end_conditions.append(cond)             
            end_conditions.append(element)
            trace.end_cond = end_conditions
            trace.show()
            print "-----------------"
            print "branch cond"
            element.show()
            print "-----------------"
            print "affected"
            for var in affected_vars:
                var.show()
            
            solve_trace_recurse(trace)
            
            break
    print "-----------------"
    print "no more"
    print 'nbs', no_branch_section
    print 'tec', trace.end_cond
    print 'var', affected_vars
    
    wp.solve_no_branch_postcond(no_branch_section, trace.end_cond, affected_vars)
