"""
Parsing infix expressions that can associate left-to-right, like
   5 - 3 - 1 (meaning: (5 - 3) - 1)
is tricky, I'm afraid, because here's the natural way to express
it in a grammar, which doesn't work:

  expr = expr (-) term   hug
       | expr
  term = (\d+)

This dies with a stack overflow because of the recursion
  expr = expr ...

By moving the recursive call over to the right, we can fix this,
at the cost of producing the wrong parse tree:

  expr = term (-) expr   hug
       | term
  term = (\d+)

This would parse it like 5-(3-1) instead. So, in the code below, we
first build the wrong tree this way, but tagging the parts that are
wrong (with misassociated()); then we fix them up in reassociate().

It's a hack. I don't see a better way without making peglet more
complex. (Ideas solicited.) (My parson package handles this nicely.)
"""

from peglet import Parser, hug

def misassociated(x, op, y):
    return 'misassoc', x, op, y

def reassociate(exp):
    if isinstance(exp, tuple) and exp[0] == 'misassoc':
        _, t, op1, rhs = exp
        while isinstance(rhs, tuple) and rhs[0] == 'misassoc':
            _, u, op2, v = rhs
            # t <op1> (u <op2> v) ==> (t <op1> u) <op2> v
            # e.g.    t - (u + v) ==> (t - u) + v
            t, op1, rhs = (t, op1, u), op2, v
        exp = t, op1, rhs
    return exp

calc = Parser(r"""
top  = _ exp0 $

exp0 = mis0                  reassociate
mis0 = exp1 ([+-]) _ mis0    misassociated
     | exp1

exp1 = mis1                  reassociate
mis1 = exp2 ([*/%]) _ mis1   misassociated
     | exp2

exp2 = term (\^) _ exp2      hug
     | term

term = (-) _ exp1            hug
     | ([\d+]) _             int
     | \( _ exp0 \) _

_    = \s*
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
