# (c) 2012 Darius Bacon
# Licensed under the GNU General Public Licence version 3
'''
Peglet extends Python's regular expressions to handle recursive
grammars. It aims to be the simplest generally-useful parsing library.

For example, to parse a tiny subset of HTML:

    >>> grammar = r"""
    ... parts = part parts | 
    ... part  = <(\w+)> parts </\w+> group
    ...       | ([^<]+)
    ... """
    >>> some_html = Parser(grammar, group=lambda *values: values)
    >>> some_html("Hello. <p><em>Nesting</em> for <i>the win</i>.</p>")
    ('Hello. ', ('p', ('em', 'Nesting'), ' for ', ('i', 'the win'), '.'))

Just as with regular expressions, we write the grammar in a raw string
(like r"") to preserve backslash characters. This grammar has two
rules, for `parts` and for `part`. `parts` matches either `part`
followed by more `parts`, or nothing (the empty string). `part`
matches either `parts` surrounded by open and close tags, or one or
more characters different from `<`.

The output is built out of regex captures (like `(\w+)`) and semantic
actions (like `group=lambda *values: values`). Here the `group`
function is called with the `(\w+)` capture along with the values
produced by the nested `parts`; then `group`'s return value becomes
the single value produced for `part`. A successful parse, in general,
always produces a tuple of values. (So for `part` the result is a
1-tuple from either `group` or `([^<]+)`; and `parts` produces a tuple
of any length, either concatenating the tuples from `part` and `parts`
or producing () for the empty string.)

Prefix matching and error handling
----------------------------------

Like `re.match`, we try to match a prefix of the input:

    >>> some_html("This <tag> has no close-tag, which our grammar insists on.")
    ('This ',)

To ensure we match the whole input, explicitly match the end with `!.`
where the `!` means to fail if the match against `.` succeeds:

    >>> full_grammar = r"html = parts !. " + grammar
    >>> some_html = Parser(full_grammar, group=lambda *values: values)

Now the ungrammatical input causes an error:

    >>> some_html("This <tag> has no close-tag, which our grammar insists on.")
    Traceback (most recent call last):
    Unparsable: ('html', 'This <tag> has no close-tag, which our grammar insists on.', '')

The `Unparsable` exception tells you the string up to the point the
error was detected at, plus the rest of the string (`''` here, which
admittedly is not much help). To get `None` from a parse failure
instead, use `attempt`:

    >>> attempt(some_html, "This <tag> has no close-tag, which our grammar insists on.")
    >>> attempt(some_html, "<i>Hi</i>")
    (('i', 'Hi'),)

(The default interface raises Unparsable because most often you do
want to know the location of parse errors.)

Grammars
--------

A peglet grammar is a kind of Parsing Expression Grammar, as explained
at http://bford.info/packrat/. Unlike in context-free grammars, the
'|' operator means *committed* choice: when parsing `a | b`, if `a`
matches, then `b` never gets checked against the same part of the
input. Also, we have a `!` operator. The syntax in detail:

A grammar is a string of rules like "a = b c | d". All the tokens
making up the rules must be whitespace-separated. Each token (besides
'=' and '|') is a regex, a rule name, or an action name. (Possibly
preceded by '!' for negation.) Note that '=' or '|' can appear inside
a regex token, but there it must not be surrounded by whitespace.

A regex token is either /<chars>/ or any non-identifier; an
identifier that's not a defined rule or action name is an
error. (So, an incomplete grammar gets you a BadGrammar exception
instead of a wrong parse.)

Matching a regex token with captures produces a tuple of all the
captured strings. Matching a sequence of tokens produces the
concatenation of the results from each. A semantic action takes all
the results produced so far for the current rule and replaces them
with one value, the result of calling the function defined for the
action (supplied as a keyword argument to the Parser constructor).
Finally, `!foo` produces only `()` on success.

Actions
-------

For convenience we supply some commonly-used semantic actions (`hug`,
`join`, and `position`).

`position` is special: it produces the current position in the string
being parsed. Special actions like this can be defined by setting
their `peglet_action` attribute; but the protocol for such actions is
undocumented.
'''

import re

def _memo(f):
    """Return a function like f but caching its results. Its arguments
    must be hashable."""
    memos = {}
    def memoized(*args):
        try: return memos[args]
        except KeyError:
            result = memos[args] = f(*args)
            return result
    return memoized

_identifier = r'[A-Za-z_]\w*'

def Parser(grammar, **actions):
    r"""Make a parsing function from a peglet grammar, defining the
    grammar's semantic actions with keyword arguments.

    The parsing function maps a string to a results tuple or raises
    Unparsable. (It can optionally take a rule name to start from, by
    default the first in the grammar.) It doesn't necessarily match
    the whole input, just a prefix.

    >>> nums = Parser(r"nums = num ,\s* nums | num   num = (\d+) int", int=int)
    >>> nums('42, 137, and 0 are magic numbers')
    (42, 137)
    >>> nums('The magic numbers are 42, 137, and 0')
    Traceback (most recent call last):
    Unparsable: ('nums', '', 'The magic numbers are 42, 137, and 0')
    """
    parts = re.split(' ('+_identifier+') += ',
                     ' '+re.sub(r'\s', ' ', grammar))
    if len(parts) == 1 or parts[0].strip():
        raise BadGrammar("Missing left hand side", parts[0])
    if len(set(parts[1::2])) != len(parts[1::2]):
        raise BadGrammar("Multiply-defined rule(s)", grammar)
    rules = dict((lhs, [alt.split() for alt in (' '+rhs+' ').split(' | ')])
                 for lhs, rhs in zip(parts[1::2], parts[2::2]))
    return lambda text, rule=parts[1]: _parse(rules, actions, rule, text)

class BadGrammar(Exception):
    "A peglet grammar was ill-formed."

class Unparsable(Exception):
    "An attempted parse failed because the input did not match the grammar."

def attempt(parse, *args, **kwargs):
    "Call a parser, but return None on failure instead of raising Unparsable."
    try: return parse(*args, **kwargs)
    except Unparsable: return None

def _parse(rules, actions, rule, text):
    # Each function takes a position pos (and maybe a values tuple
    # vals) and returns either (far, pos1, vals1) on success or (far,
    # None, ignore) on failure (where far is the rightmost position
    # reached in the attempt).

    @_memo
    def parse_rule(name, pos):
        farthest = pos
        for alternative in rules[name]:
            pos1, vals1 = pos, ()
            for token in alternative:
                far, pos1, vals1 = parse_token(token, pos1, vals1)
                farthest = max(farthest, far)
                if pos1 is None: break
            else: return farthest, pos1, vals1
        return farthest, None, ()

    def parse_token(token, pos, vals):
        if re.match(r'!.', token):
            _, pos1, _ = parse_token(token[1:], pos, vals)
            return pos, pos if pos1 is None else None, vals
        elif token in rules:
            far, pos1, vals1 = parse_rule(token, pos)
            return far, pos1, pos1 is not None and vals + vals1
        elif token in actions:
            f = actions[token]
            if hasattr(f, 'peglet_action'): return f(text, pos, vals) 
            else: return pos, pos, (f(*vals),)
        else:
            if re.match(_identifier+'$', token):
                raise BadGrammar("Missing rule", token)
            if re.match(r'/.+/$', token): token = token[1:-1]
            m = re.match(token, text[pos:])
            if m: return pos + m.end(), pos + m.end(), vals + m.groups()
            else: return pos, None, ()

    far, pos, vals = parse_rule(rule, 0)
    if pos is None: raise Unparsable(rule, text[:far], text[far:])
    else: return vals

# Some often-used actions:

def hug(*xs):
    "Return a tuple of all the arguments."
    return xs

def join(*strs):
    "Return all the arguments (strings) concatenated into one string."
    return ''.join(strs)

def position(text, pos, vals):
    "A peglet action: always succeed, producing the current position."
    return pos, pos, vals + (pos,)
position.peglet_action = True
