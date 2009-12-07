#!/usr/bin/python

import sys
from pycparser import c_parser, c_ast, parse_file

possible_error_traces = []
def error(l):
    possible_error_traces.append(l)
    
def extract_globals(decl):
    for child in decl.children():
        if isinstance(child, c_ast.TypeDecl):
            print "global variable: '%s' is %s" % (child.declname, child.type.names[0])
            return child.declname
        elif isinstance(child, c_ast.PtrDecl):
            print "global pointer: '%s' points to %s" %(decl.name, decl.type.type.type.names[0])
            return decl.name

def handle_unaryop(op, hist):
    if (op.op == "*"):
        print "deref '%s': requires '%s' non-null" % (op.expr.name, op.expr.name)
        error(hist + [op.expr] + [None])

def handle_binaryop(op, hist):
    handle_expr(op.left, hist + [op.left])
    handle_expr(op.right, hist + [op.right])

def scan_statement(stmt, hist):
    """
    Scans a statement (recursively) looking for vulnerable points
    """
    if (isinstance(stmt, c_ast.Return)):
        handle_returns(stmt, hist)
    elif (isinstance(stmt, c_ast.Assignment)):
        handle_assignment(stmt, hist)            
    elif (isinstance(stmt, c_ast.FuncCall)):
        handle_function(stmt, hist)
    elif (isinstance(stmt, c_ast.If)):
        handle_if(stmt, hist)
    else:
        print "unknown statement type: %s" % stmt

def handle_if(stmt, hist):
    handle_cond(stmt.cond, hist + [stmt.cond])
    if isinstance(stmt.iftrue, c_ast.Compound):
        handle_compound(stmt.iftrue, hist + [True] + [stmt.iftrue])
    if isinstance(stmt.iffalse, c_ast.Compound):
        handle_compound(stmt.iffalse, hist + [False] + [stmt.iffalse])

def handle_compound(compound, hist):
    for stmt in compound.stmts:
        scan_statement(stmt, hist + [stmt])
    
def handle_cond(cond, hist):
    if isinstance(cond, c_ast.UnaryOp):
        handle_unaryop(cond, hist)
    elif isinstance(cond, c_ast.BinaryOp):
        handle_binaryop(cond, hist)

def handle_assignment(stmt, hist):
    print "\n%s" % stmt.coord
    if isinstance(stmt.rvalue, c_ast.UnaryOp):
        handle_unaryop(stmt.rvalue, hist + [stmt.rvalue])
    else:
        print "read/deref", stmt.rvalue
        print hist
        
    lv = stmt.lvalue
    if isinstance(lv, c_ast.ArrayRef):
        print "write to array", lv.name.name
        print "requires 0 < '%s' < size(%s)" %(lv.subscript.name, lv.name.name)
    elif isinstance(lv, c_ast.ID):
        print "write to '%s'" % lv.name    
        
def handle_function(stmt):
    print "\n%s" % stmt.coord
    if (stmt.name.name == "printf"):
        print "call printf"
        for expr in stmt.args.exprs[1:]:
            handle_expr(expr)
        
def handle_expr(expr, hist):
    if isinstance(expr, c_ast.Constant):
        pass
    elif isinstance(expr, c_ast.ID):
        print "read '%s'" % expr.name
        print "\trequires '%s' defined" % expr.name
        print hist
    elif isinstance(expr, c_ast.UnaryOp):
        handle_unaryop(expr, hist)
    elif isinstance(expr, c_ast.BinaryOp):
        handle_binaryop(expr, hist)
            
def handle_returns(stmt, hist):
    print "%s: return" % stmt.coord
    handle_expr(stmt.expr, hist + [stmt.expr])
    if isinstance(stmt.expr, c_ast.Constant):
        pass
    elif isinstance(stmt.expr, c_ast.ID):
        print "\n%s" % stmt.coord
        print "return '%s'" % stmt.expr.name
        print "\trequires '%s' initialized or global pointer (not local)" % stmt.expr.name
