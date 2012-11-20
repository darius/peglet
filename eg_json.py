"""
Example: parse JSON.
"""

from peglet import *

literals = dict(true=True,
                false=False,
                null=None)
escapes = dict(b='\b', f='\f', n='\n', r='\r', t='\t')

mk_object = lambda *pairs: dict(pairs)
mk_literal = literals.get
escape = escapes.get
u_escape = lambda hex_digits: chr(hex(hex_digits))
mk_number = float

# Following http://www.json.org/
json_parse = Parser(r"""
start:    _ value

object:   { _ members } _        $mk_object
object:   { _ } _                $mk_object
members:  pair , _ members
members:  pair
pair:     string : _ value       $hug

array:    \[ _ elements \] _     $hug
array:    \[ _ \] _              $hug
elements: value , _ elements
elements: value

value:    string
value:    number
value:    object
value:    array
value:    (true|false|null)\b _  $mk_literal

string:   " chars " _            $join
chars:    char chars
chars:

char:     ([^\x00-0x1f"\\])
char:     \\(["/\\])
char:     \\([bfnrt])            $escape
char:     \\u xd xd xd xd  $join $u_escape

xd:       ([0-9a-fA-F])

number:   int frac exp _   $join $mk_number
number:   int frac _       $join $mk_number
number:   int exp _        $join $mk_number
number:   int _            $join $mk_number

int:      (-[1-9]) digits
int:      (-) digit
int:      ([1-9]) digits
int:      digit

frac:     ([.]) digits
exp:      ([eE][+-]?) digits

digits:   (\d+)
digit:    (\d)

_:        \s*
""", **globals())

# XXX The spec says "whitespace may be inserted between any pair of
# tokens, but leaves open just what's a token. So is the '-' in '-1' a
# token? Should I allow whitespace there?

## json_parse('true')
#. (True,)
## json_parse('"hey"')
#. ('hey',)
## json_parse('{"hey": true}')
#. ({'hey': True},)
## json_parse('[{"hey": true}]')
#. (({'hey': True},),)
## json_parse('[{"hey": true}, [-12.34]]')
#. (({'hey': True}, (-12.34,)),)

## maybe(json_parse, '{"hi"]')
