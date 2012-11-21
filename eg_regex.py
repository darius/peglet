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
literal  = repr

regex_parse = Parser(r"""
start:   exp $

exp:     term [|] exp $either
exp:     term
exp:                  $empty

term:    factor term  $chain
term:    factor

factor:  primary [*]  $star
factor:  primary [+]  $plus
factor:  primary [?]  $optional
factor:  primary

primary: \( exp \)
primary: \[ oneofs \] $join $oneof
primary: literal      $join $literal

oneofs:  oneof oneofs
oneofs:  
oneof:   \\(.)
oneof:   ([^\]])

literal: char literal
literal: char
char:    \\(.)
char:    ([^()*+?|[\]])

""", **globals())

## print regex_parse('a[xy]z()*|dc')[0]
#. (('a' ([xy] ('z' (<>)*)))|'dc')
#. 

## maybe(regex_parse, '{"hi"](')
