#!/usr/bin/python

import sys
from pycparser import c_parser, c_ast, parse_file

class Condition:
    def __init__(self, cond, istrue):
        self.cond = cond
        self.istrue = istrue
    def __repr__(self):
        return "custom" + str(self.cond) + "==" + str(self.istrue)
    def pretty(self):
        if isinstance(self.cond, c_ast.UnaryOp) and isinstance(self.cond.expr, c_ast.ID):
            print self.cond.op, self.cond.expr.name, "==", self.istrue
        else:
            self.cond.show()
    def show(self):
        self.cond.show()
        print self.istrue
    def show_affected_vars(self):
        id_list = []
        def _recurse_id(i): 
            if isinstance(i, c_ast.ID):
                id_list.append(i)
            else:
                for j in i.children():
                    _recurse_id(j)
        _recurse_id(self.cond)
        return id_list
        
class Trace(list):
    def __init__(self):
        self.end_cond = []
    def end_condition(self, cond):
        assert(isinstance(cond, Condition))
        self.end_cond.append(cond)
    def show(self):
        for i in self:
            try:
                #i.show()
                print i
            except:
                print i
        print "With end cond"
        for i in self.end_cond:
            print i

expanded_trace = Trace()

def e_include(i):
    print "*", i
    expanded_trace.append(i)
    
def e_include_assert(cond, istrue):
    print "& %s == %s" % (cond, istrue)
    expanded_trace.append(Condition(cond, istrue))
    
def e_include_end(cond, istrue):
    expanded_trace.end_condition(Condition(cond, istrue))

def expand_trace(trace):    #trace is a list
    assert(isinstance(trace[0], c_ast.FuncDef))
    expand_first(trace)
        
def expand_first(obj_list):    #expands first item of obj_list
    obj = obj_list[0]
    print "expanding " + str(obj)
    if isinstance(obj, c_ast.If):
        handle_if(obj_list)
    elif isinstance(obj, c_ast.FuncDef):
        handle_func_until(obj_list[0:], obj_list[1])
    elif isinstance(obj, c_ast.Compound):
        handle_compound_until(obj_list[0:], obj_list[1])
    elif isinstance(obj, c_ast.Assignment): #we are expanding an assignment => an assignment is in the obj_list => this is the dangerous one in question, since normally obj_list should only contain branch points (and loops in future).
        e_include_end(obj_list[-2], obj_list[-1])
    elif isinstance(obj, c_ast.ID):
        assert(len(obj_list) == 2)
        obj_list[0].show()
        print obj_list[1] 
    else:
        print "unknown type"

def handle_if(obj_list):
    e_include_assert(obj_list[0].cond, obj_list[1])
    expand_first([obj_list[2]] + obj_list[3:])
        
def handle_func_until(obj_list, until):
    func = obj_list[0]
    for stmt in func.body.stmts:
        if stmt == until:
            expand_first(obj_list[1:])
            break
        else:
            e_include(stmt)
            
def handle_compound_until(obj_list, until):
    compound = obj_list[0]
    for stmt in compound.stmts:
        if stmt == until:
            expand_first(obj_list[1:])
            break
        else:
            e_include(stmt)
