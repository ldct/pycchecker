#!/usr/bin/python

def str2py(f_args, f_body):
    s="""def func(%s):\n\t%s"""% (f_args, f_body)
    
    exec(s)
    return func
    
if __name__ == "__main__":
    f = str2py("a, b", "print a+b")
    f(1,2)
