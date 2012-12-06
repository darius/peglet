"""
Parsing infix expressions that can associate left-to-right, like
   5 - 3 - 1 (meaning: (5 - 3) - 1)
is tricky, I'm afraid, because here's the natural way to express
it in a grammar, which doesn't work:

  expr = expr (-) factor   hug
       | expr
  factor = (\d+)

This dies with a stack overflow because of the recursion
  expr = expr ...

By moving the recursive call over to the right, we can fix this,
at the cost of producing the wrong parse tree:

  expr = factor (-) expr   hug
       | factor
  factor = (\d+)

This would parse it like 5-(3-1) instead. So, in the code below, we
first build the wrong tree this way, but tagging the parts that are
wrong (with misassociated()); then we fix them up in reassociate().

It's a hack. I don't see a better way without making the parsing
library more complex. (Suggestions solicited.)
"""

from peglet import Parser, hug

def misassociated(x, op, y):
    return 'assoc', x, op, y

def reassociate(exp):
    if isinstance(exp, tuple) and exp[0] == 'assoc':
        _, t, op1, rhs = exp
        while isinstance(rhs, tuple) and rhs[0] == 'assoc':
            _, u, op2, v = rhs
            # t <op1> (u <op2> v) ==> (t <op1> u) <op2> v
            # e.g.    t - (u + v) ==> (t - u) + v
            t, op1, rhs = (t, op1, u), op2, v
        exp = t, op1, rhs
    return exp

calc = Parser(r"""
top    = _ exp0 $

exp0   = exp0a                  reassociate
exp0a  = exp1 ([+-]) _ exp0a    misassociated
       | exp1

exp1   = exp1a                  reassociate
exp1a  = exp2 ([*/%]) _ exp1a   misassociated
       | exp2

exp2   = factor (\^) _ exp2     hug
       | factor

factor = (-) _ factor           hug
       | ([\d+]) _              int
       | \( exp0 \)

_      = \s*
""", 
              int=int,
              hug=hug,
              misassociated=misassociated,
              reassociate=reassociate)

# So, operators are left-associative except ^ which associates to the right.

## calc('3')
#. (3,)
## calc('3-1')
#. ((3, '-', 1),)
## calc('3-2-1')
#. (((3, '-', 2), '-', 1),)
## calc('3/1/1')
#. (((3, '/', 1), '/', 1),)
## calc('3-1-(1-2)')
#. (((3, '-', 1), '-', (1, '-', 2)),)
## calc('2 - 4/5')
#. ((2, '-', (4, '/', 5)),)
## calc('2^3^4')
#. ((2, '^', (3, '^', 4)),)
