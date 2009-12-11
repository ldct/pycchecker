from pycparser import c_parser, c_ast
import expand_trace

def assign(a):
    assert(isinstance(a, c_ast.Assignment))
    return "%s=%s" % (c_id(a.lvalue), expr(a.rvalue))
    
def cond(c):
    assert(isinstance(c, expand_trace.Condition))
    if c.istrue:
        return expr(c.cond)
    else:
        return "not(%s)" % expr(c.cond)
    #return "return " + expr(c.cond) + "==" + str(c.istrue)


    
def c_id(i):
    try:
        assert(isinstance(i, c_ast.ID))
    except:
        raise NameError("assignment to non-id %s", i)
    return i.name
    
def expr(e):
    if isinstance(e, c_ast.UnaryOp):
        return unary(e)
    elif isinstance(e, c_ast.BinaryOp):
        return binary(e)
    elif isinstance(e, c_ast.ID):
        return e.name
    elif isinstance(e, c_ast.Constant):
        return str(e.value)
    else:
        raise NameError("unknown expr type %s" % str(e))
        
def unary(u):
    return u.op + expr(u.expr)
    
def binary(b):
    return expr(b.left) + b.op + expr(b.right) 
