"""
A bunch of small examples, some of them from the LPEG documentation.
"""

from peglet import Parser, Unparsable, attempt, hug, join, position

parse_words = Parser(r'words = \W*(\w+) words | ')

# The equivalent re.split() would return extra '' results first and last:
## parse_words('"Hi, there", he said.')
#. ('Hi', 'there', 'he', 'said')

def Tag(label):
    return lambda *parts: (label,) + parts

name = Parser(r"""
name    = title first middle last
title   = title_ Title _ |
title_  = (Dr|Mr|Ms|Mrs|St)[.]? | (Pope(?:ss)?)
first   = ([A-Za-z]+) First _
middle  = middle_ Middle _ |
middle_ = ([A-Z])[.] | ([A-Za-z]+)
last    = ([A-Za-z]+) Last
_       = \s+
""",
              Title  = Tag('title'),
              First  = Tag('first'),
              Middle = Tag('middle'),
              Last   = Tag('last'))
## name('Popess Darius Q. Bacon')
#. (('title', 'Popess'), ('first', 'Darius'), ('middle', 'Q'), ('last', 'Bacon'))

ichbins = Parser(r"""
main     =  _ sexp

sexp     =  \\(.)         _ lit_char
         |  " qchars "    _ join
         |  symchars      _ join
         |  ' _ sexp        quote
         |  \( _ sexps \) _ hug

sexps    =  sexp sexps
         |

qchars   =  \\(.) qchars
         |  ([^"]) qchars
         |  

symchars =  symchar symchars
         |  symchar
symchar  =  ([^\s\\"'()])

_        =  \s*
""",
                 lit_char = ord,
                 join     = join,
                 quote    = lambda x: ('quote', x),
                 hug      = hug)

## ichbins('() (hey)', rule='sexps')
#. ((), ('hey',))

## ichbins('hi')
#. ('hi',)
## ichbins(r"""(hi '(john mccarthy) \c )""")
#. (('hi', ('quote', ('john', 'mccarthy')), 99),)
## ichbins(r""" ""  """)
#. ('',)
## ichbins(r""" "hey"  """)
#. ('hey',)

# From http://www.inf.puc-rio.br/~roberto/lpeg/

as_and_bs = Parser(r"""
allS = S $

S    = /a/ B
     | /b/ A
     |

A    = /a/ S
     | /b/ A A

B    = /b/ S
     | /a/ B B
""")

## as_and_bs("abaabbbbaa")
#. ()

nums = Parser(r"""
allnums =   nums $

nums    = num , nums
        | num
        | 

num     = ([0-9]+) int
""",
              int=int)
sum_nums = lambda s: sum(nums(s))

## sum_nums('10,30,43')
#. 83

one_word = Parser(r"word = \w+ position", position=position)

## one_word('hello')
#. (5,)
## one_word('hello there')
#. (5,)
## attempt(one_word, ' ')

namevalues = Parser(r"""
list   =  _ pairs $
pairs  =  pair pairs
       |
pair   =  name [=] _ name [,;]? _   hug
name   =  (\w+) _
_      =  \s*
""", **globals())
namevalues_dict = lambda s: dict(namevalues(s))
## namevalues_dict("a=b, c = hi; next = pi")
#. {'a': 'b', 'c': 'hi', 'next': 'pi'}

# Splitting a string. But with lpeg it's parametric over a pattern p.
# NB this assumes p doesn't match '', and that it doesn't capture.

splitting = Parser(r"""
split  =  p split
       |  chunk join split
       |  
chunk  =  p
       |  (.) chunk
p      =  \s
""", **globals())
## splitting('hello a world  is    nice    ')
#. ('hello', 'a', 'world', 'is', 'nice')

# Searching for a pattern: also parameterized by p.
# (skipped)

balanced_parens = Parser(r"""
bal  =  \( cs \)
cs   =  c cs
     |  
c    =  [^()]
     |  bal
""")

## attempt(balanced_parens, '()')
#. ()
## attempt(balanced_parens, '(()')

# gsub: another parameterized one

gsub = lambda text, replacement: ''.join(Parser(r"""
gsub =  p gsub
     |  (.) gsub
     |    
p    =  /WHEE/ replace
""", replace=lambda: replacement)(text))

## gsub('hi there WHEEWHEE to you WHEEEE', 'GLARG')
#. 'hi there GLARGGLARG to you GLARGEE'

csv = Parser(r"""
record =   field fields !.
fields =   , field fields
       |   

field  =   " qchars "\s* join
       |   ([^,"\n]*)

qchars =   qchar qchars
       |               
qchar  =   ([^"])
       |   "" dquote
""",
             join = join,
             dquote = lambda: '"')

## csv('')
#. ('',)
## csv('""')
#. ('',)
## csv("""hi,there,,"this,isa""test"   """)
#. ('hi', 'there', '', 'this,isa"test')


## Parser('x = ')('')
#. ()

def p(grammar, text, **kwargs):
    parse = Parser(grammar, **globals())
    try:
        return parse(text, **kwargs)
    except Unparsable, e:
        return e

metagrammar = r"""
grammar       =  _ rules
rules         =  rule rules
              |  rule
rule          =  name [=] _ expr \. _       make_rule
expr          =  term \| _ expr             alt
              |  term
term          =  factors : _ name           reduce_
              |  factors
factors       =  factor factors             seq
              |                             empty
factor        =  '((?:\\.|[^'])*)' _        literal
              |  name                       rule_ref
name          =  (\w+) _
_             =  \s*
"""

def make_rule(name, expr): return '%s: %s' % (name, expr)
def alt(e1, e2):           return '%s/%s' % (e1, e2)
def reduce_(e, name):      return '%s =>%s' % (e, name)
def seq(e1, *e2):          return '%s+%s' % ((e1,) + e2) if e2 else e1
def empty():               return '<>'
def literal(regex):        return '/%s/' % regex
def rule_ref(name):        return '<%s>' % name

## p(metagrammar, ' hello = bargle. goodbye = hey there.aloha=.')
#. ('hello: <bargle>+<>', 'goodbye: <hey>+<there>+<>', 'aloha: <>')
## p(metagrammar, ' hello arg = bargle.')
#. Unparsable('grammar', ' hello ', 'arg = bargle.')
## p(metagrammar, "'goodbye' world", rule='term')
#. ('/goodbye/+<world>+<>',)

bal = r"""
allbalanced =  _ bal !.
_           =  \s*
bal         =  \( _ bal \) _ hug bal
            |  (\w+) _
            |
"""
## p(bal, '(x) y')
#. (('x',), 'y')
## p(bal, 'x y')
#. Unparsable('allbalanced', 'x ', 'y')

curl = r"""
one_expr =  _ expr $
_        =  \s*
expr     =  { _ exprs } _ hug
         |  ([^{}\s]+) _
exprs    =  expr exprs
         |
"""
## p(curl, '')
#. Unparsable('one_expr', '', '')
## p(curl, '{}')
#. ((),)
## p(curl, 'hi')
#. ('hi',)
## p(curl, '{hi {there} {{}}}')
#. (('hi', ('there',), ((),)),)

multiline_rules = r"""
hi =  /this/ /is/
      /a/ /rule/
   |  /or/ /this/
"""

## p(multiline_rules, "thisisarule")
#. ()
## p(multiline_rules, "orthis")
#. ()
## p(multiline_rules, "thisisnot")
#. Unparsable('hi', 'thisis', 'not')
