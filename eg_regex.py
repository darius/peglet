"""
Example: parse regular expressions.
"""

from peglet import *

empty    = lambda: '<>'
chain    = lambda p, q: '(%s %s)' % (p, q)
either   = lambda p, q: '(%s|%s)' % (p, q)
star     = lambda p: '(%s)*' % p
plus     = lambda p: '(%s)+' % p
optional = lambda p: '(%s)?' % p
oneof    = lambda chars: '[%s]' % chars
someone  = lambda: '.'
literal  = repr

regex_parse = Parser(r"""
start:   exp $

exp:     term [|] exp    $either
exp:     term
exp:                     $empty

term:    factor term     $chain
term:    factor

factor:  primary [*]     $star
factor:  primary [+]     $plus
factor:  primary [?]     $optional
factor:  primary

primary: \( exp \)
primary: \[ charset \]   $join $oneof
primary: [.]             $someone
primary: \\(.)           $literal
primary: ([^.()*+?|[\]]) $literal

charset: char charset
charset: 
char:    \\(.)
char:    ([^\]])

""", **globals())

## print regex_parse('a[xy]z()*|dc..hello')[0]
#. (('a' ([xy] ('z' (<>)*)))|('d' ('c' (. (. ('h' ('e' ('l' ('l' 'o')))))))))
#. 

## maybe(regex_parse, '{"hi"](')
