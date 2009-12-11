#!/usr/bin/python

def function(f_args, f_body):
    s="""def func(%s):\n"""% f_args
    for stmt in f_body:
        s+="\t%s\n" % stmt
    
    exec(s)
    return func
    
if __name__ == "__main__":
    f = function("a, b", ["b=3","print a+b"])
    f(1,2)
