"""
Example: parse JSON.
"""

from peglet import Parser, hug, join, attempt

literals = dict(true=True,
                false=False,
                null=None)
mk_literal = literals.get

mk_object  = lambda *pairs: dict(pairs)
escape     = lambda s: s.decode('unicode-escape')
mk_number  = float

# Following http://www.json.org/
json_parse = Parser(r"""
start    = _ value

object   = { _ members } _        mk_object
         | { _ } _                mk_object
members  = pair , _ members
         | pair
pair     = string : _ value       hug

array    = \[ _ elements \] _     hug
         | \[ _ \] _              hug
elements = value , _ elements
         | value

value    = string | number
         | object | array
         | (true|false|null)\b _  mk_literal

string   = " chars " _            join
chars    = char chars
         |
char     = ([^\x00-\x1f"\\])
         | \\(["/\\])
         | (\\[bfnrt])            escape
         | (\\u) xd xd xd xd join escape
xd       = ([0-9a-fA-F])

number   = int frac exp _    join mk_number
         | int frac _        join mk_number
         | int exp _         join mk_number
         | int _             join mk_number
int      = (-?) (0) !\d
         | (-?) ([1-9]\d*)
frac     = ([.]\d+)
exp      = ([eE][+-]?\d+)

_        = \s*
""", **globals())

# XXX The spec says "whitespace may be inserted between any pair of
# tokens, but leaves open just what's a token. So is the '-' in '-1' a
# token? Should I allow whitespace there?

## json_parse('[1,1]')
#. ((1.0, 1.0),)
## json_parse('true')
#. (True,)
## json_parse(r'"hey \b\n \u01ab o hai"')
#. (u'hey \x08\n \u01ab o hai',)
## json_parse('{"hey": true}')
#. ({'hey': True},)
## json_parse('[{"hey": true}]')
#. (({'hey': True},),)
## json_parse('[{"hey": true}, [-12.34]]')
#. (({'hey': True}, (-12.34,)),)
## json_parse('0')
#. (0.0,)
## json_parse('0.125e-2')
#. (0.00125,)

## attempt(json_parse, '0377')
## attempt(json_parse, '{"hi"]')

# Udacity CS212 problem 3.1:

## json_parse('["testing", 1, 2, 3]')
#. (('testing', 1.0, 2.0, 3.0),)

## json_parse('-123.456e+789')
#. (-inf,)

## json_parse('{"age": 21, "state":"CO","occupation":"rides the rodeo"}')
#. ({'age': 21.0, 'state': 'CO', 'occupation': 'rides the rodeo'},)
