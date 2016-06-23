"""
Parsing infix expressions that associate left-to-right, like
   5 - 3 - 1 (meaning: (5 - 3) - 1)
is a little tricky, because the natural way to express it in a
grammar, like this, doesn't work:

  expr = expr (-) term   hug
       | expr
  term = (\d+)

This dies with a stack overflow because the recursion
  expr = expr ...
precedes any base case.

Moving the recursive call over to the right would fix the problem,
at the cost of producing the wrong parse tree, a tree like 5-(3-1):

  expr = term (-) expr   hug
       | term

So the code below instead takes the form

  expr = term ops
  ops  = (-) term ops
       | 

plus semantic actions that juggle the values into place. (My
other parsing library, Parson, can manage without the juggling.)
"""

from peglet import Parser, OneResult, hug

def apply(a, f):   return f(a)
def rhs(op, b):    return lambda a: (a, op, b)
def compose(f, g): return lambda a: g(f(a))
def identity():    return lambda a: a

g = r"""
top   =  _ exp0 $

exp0  =  exp1 ops0 apply 
ops0  =  ([+-]) _ exp1 rhs ops0 compose
      |  identity

exp1  =  exp2 ops1 apply
ops1  =  ([*/%]) _ exp2 rhs ops1 compose
      |  identity

exp2 = term (\^) _ exp2      hug
     | term

term  =  (-) _ exp1          hug
      |  \( _ exp0 \) _
      |  (\d+) _             int

_     =  \s*
"""

calc = OneResult(Parser(g, int=int, **globals()))

## calc('3')
#. 3
## calc('3-1')
#. (3, '-', 1)
## calc('5-4-3-2-1')
#. ((((5, '-', 4), '-', 3), '-', 2), '-', 1)
## calc('60/5/6')
#. ((60, '/', 5), '/', 6)
## calc('3-1-(1-2)')
#. ((3, '-', 1), '-', (1, '-', 2))
## calc('2 - 4/5')
#. (2, '-', (4, '/', 5))
## calc('2^3^4')
#. (2, '^', (3, '^', 4))
