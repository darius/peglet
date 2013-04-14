"""
A concatenative variant of John Backus's FP language.
http://en.wikipedia.org/wiki/FP_%28programming_language%29
"""

from peglet import Parser

program = {}

primitives = dict(transpose = lambda arg: zip(*arg),
                  distl = lambda (x, ys): [[x, y] for y in ys],
                  distr = lambda (xs, y): [[x, y] for x in xs],
                  iota = lambda n: range(1, n+1),)

add = lambda (x, y): x+y
sub = lambda (x, y): x-y
mul = lambda (x, y): x*y
div = lambda (x, y): x/y

ops = {'+': add, '-': sub, '*': mul, '/': div,}

def function_identity(f):
    if f in (add, sub): return 0
    if f in (mul, div): return 1
    raise Exception("No known identity element", f)

def mk_program(*defs): return dict(defs)
def mk_def(name, exp): return (name, exp)
def mk_if(c, t, e):    return lambda arg: (t if c(arg) else e)(arg)
def mk_compose(e, f):  return lambda arg: f(e(arg))
def mk_map(f):         return lambda arg: map(f, arg)
def mk_insertl(f):     return lambda arg: insertl(f, arg)
def mk_insertr(f):     return lambda arg: insertr(f, arg)
def mk_aref(n):        return lambda arg: arg[n-1]
def mk_literal(n):     return lambda _: n
def mk_call(name):     return lambda arg: program[name](arg)
def mk_op(name):       return ops[name]
def mk_list(*exps):    return lambda arg: [f(arg) for f in exps]

def insertl(f, xs):
    if not xs: return function_identity(f)
    return reduce(lambda x, y: f([x, y]), xs)

def insertr(f, xs):
    if not xs: return function_identity(f)
    z = xs[-1]
    for x in xs[-1::-1]:
        z = f([x, z])
    return z

fp_parse = Parser(r"""
program = _ defs $                 mk_program

defs    = def defs
        | 
def     = name == _ exp [.] _      mk_def

exp     = term -> _ term ; _ exp   mk_if
        | term

term    = factor term              mk_compose
        | factor

factor  = @ _ factor               mk_map
        | / _ factor               mk_insertr
        | \\ _ factor              mk_insertl
        | primary

primary = decimal                  mk_aref
        | ~ _ integer              mk_literal
        | name                     mk_call
        | ([*+/-]) _               mk_op
        | \[ _ list \] _           mk_list
        | \( _ exp \) _

list    = exp , _ list
        | exp
        |

decimal = (\d+) _                  int
integer = (-?\d+) _                int
name    = ([A-Za-z]\w*) _

_       = \s*

""", int=int, **globals())


examples = r"""
factorial == iota \*.
dot == transpose @* \+.
matmult == [1, 2 transpose] distr @distl @@dot.
"""
## program = fp_parse(examples)[0]
## program.update(primitives)
## factorial, dot, matmult = map(program.get, 'factorial dot matmult'.split())

## factorial(0)
#. 1
## factorial(5)
#. 120

## dot([[1,2], [3,4]])
#. 11
## dot([])
#. 0

## matmult([ [], [] ])
#. []
## matmult([ [[4]], [[5]] ])
#. [[20]]
## matmult([ [[2,0],[0,2]], [[5,6],[7,8]] ])
#. [[10, 12], [14, 16]]
## matmult([ [[0,1],[1,0]], [[5,6],[7,8]] ])
#. [[7, 8], [5, 6]]
