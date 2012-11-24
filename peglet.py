"""
Parsing with PEGs, or a minimal usable subset thereof.
"""

import re

def _memo(f):
    memos = {}
    def memoized(*args):
        try: return memos[args]
        except KeyError:
            result = memos[args] = f(*args)
            return result
    return memoized

_identifier = r'[A-Za-z_]\w*'

def Parser(grammar, **actions):
    r"""Make a parsing function from a PEG grammar. You supply the
    grammar as a string of rules like "a = b c | d". All the tokens
    making up the rules must be whitespace-separated. Each token
    (besides '=' and '|') is a regex, a rule name, or an action
    name. (Possibly preceded by '!' for negation: !foo successfully
    parses when foo *fails* to parse.)

    A regex token is either /<chars>/ or any non-identifier; an
    identifier that's not a defined rule or action name is an
    error. (So, an incomplete grammar gets you a BadGrammar exception
    instead of a wrong parse.)

    Results get added by regex captures and transformed by actions.
    (Use keyword arguments to bind the action names to functions.)

    The parsing function maps a string to a results tuple or raises
    Unparsable. (It can optionally take a rule name to start from, by
    default the first in the grammar.) It doesn't necessarily match
    the whole input, just a prefix.

    >>> parse_s_expression = Parser(r'''
    ... one_expr = _ expr !.
    ... _        = \s*
    ... expr     = \( _ exprs \) _  hug
    ...          | ([^()\s]+) _
    ... exprs    = expr exprs
    ...          | ''',             hug = lambda *vals: vals)
    >>> parse_s_expression('  (hi (john mccarthy) (()))')
    (('hi', ('john', 'mccarthy'), ((),)),)
    >>> parse_s_expression('(too) (many) (exprs)')
    Traceback (most recent call last):
    Unparsable: ('one_expr', '(too) ', '(many) (exprs)')
    """
    parts = re.split(r'\s('+_identifier+')\s+=\s', ' '+grammar)
    if not parts: raise BadGrammar("No grammar")
    if parts[0].strip(): raise BadGrammar("Missing left hand side", parts[0])
    if len(set(parts[1::2])) != len(parts[1::2]):
        raise BadGrammar("Multiply-defined rule(s)", grammar)
    rules = dict((lhs, [alt.split() for alt in re.split(r'\s[|](?:\s|$)', rhs)])
                 for lhs, rhs in zip(parts[1::2], parts[2::2]))
    return lambda text, rule=parts[1]: _parse(rules, actions, rule, text)

class BadGrammar(Exception): pass
class Unparsable(Exception): pass

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
            if pos1 is not None: return farthest, pos1, vals1
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
            if hasattr(f, 'is_peg'): return f(text, pos, vals) 
            else: return pos, pos, (f(*vals),)
        else:
            if re.match(_identifier+'$', token):
                raise BadGrammar("Missing rule: %s" % token)
            if re.match(r'/.+/$', token): token = token[1:-1]
            m = re.match(token, text[pos:])
            if m: return pos + m.end(), pos + m.end(), vals + m.groups()
            else: return pos, None, ()

    far, pos, vals = parse_rule(rule, 0)
    if pos is None: raise Unparsable(rule, text[:far], text[far:])
    else: return vals

# Some often-used actions:
def hug(*xs): return xs
def join(*strs): return ''.join(strs)

def position(text, pos, vals):
    return pos, pos, vals + (pos,)
position.is_peg = True
