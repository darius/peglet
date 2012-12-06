from operator import *
from peglet import *

def reassociate(exp):
    if len(exp) == 3:
        x, op1, y = exp
        if len(y) == 3:
            u, op2, v = y
            # x - (u + v) -> (x - u) + v
            return reassociate(((x, op1, u), op2, v))
        else:
            assert len(y) == 1
            return (x, op1, y[0])
    else:
        assert len(exp) == 1
        return exp[0]

calc = Parser(r"""
top    = _ exp $

exp    = exp0                   reassociate
exp0   = factor ([+-]) _ exp0   hug
       | factor                 hug              

factor = (-) _ factor           hug
       | ([\d+])                int
       | \( exp \)

_      = \s*
""", 
              int=int,
              hug=hug,
              reassociate=reassociate)

## calc('3-1-(1-2)')
#. (((3, '-', 1), '-', (1, '-', 2)),)
