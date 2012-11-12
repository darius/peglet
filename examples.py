from peglet import Parser, maybe, chunk, cat, position

ichbins = Parser(r"""
main      _ sexp

sexp      \\(.)         _ :lit_char
sexp      " qchars "    _ :cat
sexp      symchars      _ :cat
sexp      ' _ sexp        :quote
sexp      \( _ sexps \) _ :chunk

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
                 lit_char = lambda c: '\\' + c,
                 cat      = lambda *xs: ''.join(xs),
                 quote    = lambda x: ('quote', x),
                 chunk    = chunk)

## ichbins('() (hey)', rule='sexps')
#. ((), ('hey',))

## ichbins('hi')
#. ('hi',)
## ichbins(r"""(hi '(john mccarthy) \c )""")
#. (('hi', ('quote', ('john', 'mccarthy')), '\\c'),)
## ichbins(r""" ""  """)
#. ('',)
## ichbins(r""" "hey"  """)
#. ('hey',)

# From http://www.inf.puc-rio.br/~roberto/lpeg/

as_and_bs = Parser(r"""
allS   S $

S   a B
S   b A
S 

A   a S
A   b A A

B   b S
B   a B B
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

# TODO lpeg gives the position after the match, or None:
## one_word('hello')
#. (5,)
## one_word('hello there')
#. (5,)
## one_word(' ')
#. Traceback (most recent call last):
#.   File "/home/darius/git/peglet/peglet.py", line 50, in parse
#.     else: raise Unparsable(rule, (text[:utmost[0]], text[utmost[0]:]))
#. Unparsable: ('word', ('', ' '))

namevalues = Parser(r"""
list    _ pairs $
pairs   pair pairs
pairs 
pair    name = _ name [,;]? _   :chunk
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
split   chunk :cat split
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
p       WHEE :replace
""", replace=lambda: replacement)(text))

## gsub('hi there WHEEWHEE to you WHEEEE', 'GLARG')
#. 'hi there GLARGGLARG to you GLARGEE'

csv = Parser(r"""
record   field fields $
fields   , field fields
fields   

field    " qchars "\s* :cat
field    ([^,"\n]*)

qchars   qchar qchars
qchars               
qchar    ([^"])
qchar    "" :dquote
""", 
             cat = cat,
             dquote = lambda: '"')

## csv('')
#. ('',)
## csv('""')
#. ('',)
## csv("""hi,there,,"this,isa""test"   """)
#. ('hi', 'there', '', 'this,isa"test')
