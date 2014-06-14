r"""
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
parse the wrong way, but fix up the tree as we build it, with 
reassociate(). Shelter protects subtrees from this reassociation.

It's a hack. I don't see a better way without making peglet more
complex. (Ideas solicited.) (My parson package handles this nicely.)
"""

from peglet import Parser, hug

class Shelter:
    def __init__(self, exp):
        self.sheltered = expose(exp)

def expose(exp):
    return exp.sheltered if isinstance(exp, Shelter) else exp

def reassociate(x, op, y):
    "x-(u-v) => (x-u)-v and recursively."
    x = expose(x)
    if isinstance(y, tuple):
        return reassociate(x, op, y[0]), y[1], expose(y[2])
    else:
        return x, op, expose(y)

parse = Parser(r"""
top  = _ exp0 $

exp0 = exp1 ([+-]) _ exp0    reassociate
     | exp1                  Shelter

exp1 = exp2 ([*/%]) _ exp1   reassociate
     | exp2                  Shelter

exp2 = term (\^) _ exp2      hug
     | term

term = (-) _ exp1            hug
     | ([\d+]) _             int
     | \( _ exp0 \) _

_    = \s*
""", 
              int=int,
              hug=hug,
              Shelter=Shelter,
              reassociate=reassociate)

def calc(s):
    exp, = parse(s)
    return expose(exp)

# So, operators are left-associative except ^ which associates to the right.

## calc('3')
#. 3
## calc('3-1')
#. (3, '-', 1)
## calc('5-4-3-2-1')
#. ((((5, '-', 4), '-', 3), '-', 2), '-', 1)
## calc('3/1/1')
#. ((3, '/', 1), '/', 1)
## calc('3-1-(1-2)')
#. ((3, '-', 1), '-', (1, '-', 2))
## calc('2 - 4/5')
#. (2, '-', (4, '/', 5))
## calc('2^3^4')
#. (2, '^', (3, '^', 4))
