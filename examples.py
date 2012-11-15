from peglet import Parser, maybe, hug, join, position

ichbins = Parser(r"""
main      _ sexp

sexp      \\(.)         _ :lit_char
sexp      " qchars "    _ :join
sexp      symchars      _ :join
sexp      ' _ sexp        :quote
sexp      \( _ sexps \) _ :hug

sexps     sexp sexps
sexps

qchars    \\(.) qchars
qchars    ([^"]) qchars
qchars    

symchars  symchar symchars
symchars  symchar
symchar   ([^\s\\"'()])

_         \s*
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
allS   S $

S   /a B
S   /b A
S 

A   /a S
A   /b A A

B   /b S
B   /a B B
""")

## as_and_bs("abaabbbbaa")
#. ()

nums = Parser(r"""
allnums   nums $

nums   num , nums
nums   num
nums   

num    ([0-9]+) :int
""",
              int=int)
sum_nums = lambda s: sum(nums(s))

## sum_nums('10,30,43')
#. 83

one_word = Parser("word \w+ ::position", **globals())

## one_word('hello')
#. (5,)
## one_word('hello there')
#. (5,)
## maybe(one_word, ' ')

namevalues = Parser(r"""
list    _ pairs $
pairs   pair pairs
pairs 
pair    name = _ name [,;]? _   :hug
name    (\w+) _
_       \s*
""", **globals())
namevalues_dict = lambda s: dict(namevalues(s))
## namevalues_dict("a=b, c = hi; next = pi")
#. {'a': 'b', 'c': 'hi', 'next': 'pi'}

# Splitting a string. But with lpeg it's parametric over a pattern p.
# NB this assumes p doesn't match ''.

splitting = Parser(r"""
split   p split
split   chunk :join split
split   
chunk   p
chunk   (.) chunk
p       \s
""", **globals())
## splitting('hello a world  is    nice    ')
#. ('hello', 'a', 'world', 'is', 'nice')

# Searching for a pattern: also parameterized by p.
# (skipped)

balanced_parens = Parser(r"""
bal   \( cs \)
cs    c cs
cs    
c     [^()]
c     bal
""")

## maybe(balanced_parens, '()')
#. ()
## maybe(balanced_parens, '(()')

# gsub: another parameterized one

gsub = lambda text, replacement: ''.join(Parser(r"""
gsub    p gsub
gsub    (.) gsub
gsub    
p       /WHEE :replace
""", replace=lambda: replacement)(text))

## gsub('hi there WHEEWHEE to you WHEEEE', 'GLARG')
#. 'hi there GLARGGLARG to you GLARGEE'

csv = Parser(r"""
record   field fields $
fields   , field fields
fields   

field    " qchars "\s* :join
field    ([^,"\n]*)

qchars   qchar qchars
qchars               
qchar    ([^"])
qchar    "" :dquote
""", 
             join = join,
             dquote = lambda: '"')

## csv('')
#. ('',)
## csv('""')
#. ('',)
## csv("""hi,there,,"this,isa""test"   """)
#. ('hi', 'there', '', 'this,isa"test')
