from peglet import *

## Grammar('x')('')
#. ()

def p(grammar, text, **kwargs):
    parse = Grammar(grammar, **globals())
    try: 
        return parse(text, **kwargs)
    except Unparsable, e:
        return e

metagrammar = r"""
grammar         _ rules
rules           rule rules               
rules           rule
rule            name = _ expr \. _         :make_rule
expr            term \| _ expr             :alt
expr            term
term            factors [:] _ name         :reduce_
term            factors
factors         factor factors             :seq
factors                                    :empty
factor          '((?:\\.|[^'])*)' _        :literal
factor          name                       :rule_ref
name            (\w+) _
_               \s*
"""

def make_rule(name, expr): return '%s: %s' % (name, expr)
def alt(e1, e2):           return '%s/%s' % (e1, e2)
def reduce_(e, name):      return '%s =>%s' % (e, name)
def seq(e1, *e2):          return '%s+%s' % ((e1,) + e2) if e2 else e1
def empty():               return '<>'
def literal(regex):        return '/%s/' % regex
def rule_ref(name):        return '<%s>' % name

wrap = lambda *vals: vals

## p(metagrammar, ' hello = bargle. goodbye = hey there.aloha=.')
#. ('hello: <bargle>+<>', 'goodbye: <hey>+<there>+<>', 'aloha: <>')
## p(metagrammar, ' hello arg = bargle.')
#. Unparsable('grammar', (' hello ', 'arg = bargle.'))
## p(metagrammar, "'goodbye' world", rule='term')
#. ('/goodbye/+<world>+<>',)

bal = r"""
allbalanced   _ bal !.
_             \s*
bal           \( _ bal \) _ :wrap bal
bal           (\w+) _
bal
"""
## p(bal, '(x) y')
#. (('x',), 'y')
## p(bal, 'x y')
#. Unparsable('allbalanced', ('x ', 'y'))

curl = r"""
one_expr   _ expr !.
_          \s*
expr       { _ exprs } _ :wrap
expr       ([^{}\s]+) _
exprs      expr exprs
exprs
"""
## p(curl, '')
#. Unparsable('one_expr', ('', ''))
## p(curl, '{}')
#. ((),)
## p(curl, 'hi')
#. ('hi',)
## p(curl, '{hi {there} {{}}}')
#. (('hi', ('there',), ((),)),)
