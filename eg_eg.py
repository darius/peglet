from peglet import Parser, maybe, hug, join, position
from peglet import parse_grammar, extend, parse

ichbins_rules = extend(parse_grammar(r"""
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
"""),
                 lit_char = ord,
                 join     = join,
                 quote    = lambda x: ('quote', x),
                 hug      = hug)
ichbins = lambda text: parse(ichbins_rules, text)
## parse(('sexps', ichbins_rules), '() (hey)')
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

S    = /a B
     | /b A
     |

A    = /a S
     | /b A A

B    = /b S
     | /a B B
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

one_word = Parser("word = \w+ position", position=position)

## one_word('hello')
#. (5,)
## one_word('hello there')
#. (5,)
## maybe(one_word, ' ')

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

## maybe(balanced_parens, '()')
#. ()
## maybe(balanced_parens, '(()')

# gsub: another parameterized one

gsub = lambda text, replacement: ''.join(Parser(r"""
gsub =  p gsub
     |  (.) gsub
     |    
p    =  /WHEE replace
""", replace=lambda: replacement)(text))

## gsub('hi there WHEEWHEE to you WHEEEE', 'GLARG')
#. 'hi there GLARGGLARG to you GLARGEE'

csv = Parser(r"""
record =   field fields $
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
