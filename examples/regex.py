"""
Example: parse regular expressions.
"""

from peglet import *

empty    = lambda: '""'
chain    = lambda p, q: '(%s %s)' % (p, q)
either   = lambda p, q: '(%s|%s)' % (p, q)
star     = lambda p: '(%s)*' % p
plus     = lambda p: '(%s)+' % p
optional = lambda p: '(%s)?' % p
oneof    = lambda chars: '[%s]' % chars
someone  = lambda: '.'
literal  = repr

regex_parse = Parser(r"""
start   = exp $

exp     = term [|] exp    either
        | term
        |                 empty

term    = factor term     chain
        | factor

factor  = primary [*]     star
        | primary [+]     plus
        | primary [?]     optional
        | primary

primary = \( exp \)
        | \[ charset \]   join oneof
        | [.]             someone
        | \\(.)           literal
        | ([^.()*+?|[\]]) literal

charset = char charset
        |
char    = \\(.)
        | ([^\]])

""", **globals())

## print regex_parse('a[xy]z()*|dc..hello')[0]
#. (('a' ([xy] ('z' ("")*)))|('d' ('c' (. (. ('h' ('e' ('l' ('l' 'o')))))))))
#. 

## attempt(regex_parse, '{"hi"](')
