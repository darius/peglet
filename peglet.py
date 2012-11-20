"""
Parsing with PEGs, or a minimal usable subset thereof.
"""

import collections, re

def Parser(grammar, **actions):
    r"""Make a parsing function from a PEG grammar. You supply the
    grammar as a string with one line per alternative, like the
    example grammar below. Each line starts with the name of the rule
    it defines an alternative for; each following token is a regex, a
    rule name, or an action name. (Possibly preceded by '!' for
    negation: !foo successfully parses when foo *fails* to parse.)

    Results get added by regex captures and transformed by actions
    (which are named like '$hug' below; to say what 'hug' means
    here, make it a keyword argument).

    A regex token in the grammar either starts with '/' or is a
    non-identifier token. An identifier that's not a defined rule name
    is an error. (So, when you write an incomplete grammar, you get a
    BadGrammar exception instead of a failure to parse.)

    Actions named like '$$action' get raw access to the parsing state.

    The parsing function maps a string a results tuple or raises
    Unparsable. (It can optionally take a rule name to start from, by
    default the first in the grammar.) It doesn't necessarily match
    the whole input, just a prefix.

    >>> parse_s_expression = Parser(r'''
    ... one_expr:   _ expr !.
    ... _:          \s*
    ... expr:       \( _ exprs \) _ $hug
    ... expr:       ([^()\s]+) _
    ... exprs:      expr exprs
    ... exprs:      ''',             hug = lambda *vals: vals)
    >>> parse_s_expression('  (hi (john mccarthy) (()))')
    (('hi', ('john', 'mccarthy'), ((),)),)
    >>> parse_s_expression('(too) (many) (exprs)')
    Traceback (most recent call last):
    Unparsable: ('one_expr', '(too) ', '(many) (exprs)')
    """
    parts = re.split(r'\n(\w+):', '\n'+grammar)
    if not parts: raise BadGrammar("No grammar")
    if parts[0].strip(): raise BadGrammar("Missing left-hand-side")
    rules = collections.defaultdict(list)
    for i in range(1, len(parts), 2):
        rules[parts[i]].append(parts[i+1].split())
    return lambda text, rule=parts[1]: _parse(rules, actions, rule, text)

# A parsing state: a position in the input text and a values tuple.
State = collections.namedtuple('State', 'pos vals'.split())

def _parse(rules, actions, rule, text):
    # Each parsing function starts from a pos in text and returns
    # either None (failure) or an updated state. We also track utmost:
    # a mutable box holding the rightmost position positively reached.

    memos = {}
    def parse_rule(name, utmost, pos):
        try: return memos[name, pos]
        except KeyError:
            result = memos[name, pos] = really_parse_rule(name, utmost, pos)
            return result

    def really_parse_rule(name, utmost, pos):
        for alternative in rules[name]:
            st = parse_sequence(alternative, utmost, pos)
            if st: return st
        return None

    def parse_sequence(tokens, utmost, pos):
        st = State(pos, ())
        for token in tokens:
            st = parse_token(token, utmost, st)
            if not st: break
        return st

    def parse_token(token, utmost, st):
        if token.startswith('$$'):
            return actions[token[2:]](rules, text, utmost, st)
        elif re.match(r'[$]\w+$', token):
            return State(st.pos, (actions[token[1:]](*st.vals),))
        elif token.startswith('!'):
            return None if parse_token(token[1:], [0], st) else st
        elif token in rules:
            st2 = parse_rule(token, utmost, st.pos)
            return State(st2.pos, st.vals + st2.vals) if st2 else None
        else:
            if re.match(r'[A-Za-z_]\w*$', token):
                raise BadGrammar("Missing rule: %s" % token)
            if re.match(r'/.', token): token = token[1:]
            m = re.match(token, text[st.pos:])
            if not m: return None
            utmost[0] = max(utmost[0], st.pos + m.end())
            return State(st.pos + m.end(), st.vals + m.groups())

    utmost = [0]
    st = parse_rule(rule, utmost, 0)
    if st: return st.vals
    else: raise Unparsable(rule, text[:utmost[0]], text[utmost[0]:])

class Unparsable(Exception): pass
class BadGrammar(Exception): pass

def maybe(parse, *args, **kwargs): # XXX rename to 'attempt'?
    try: return parse(*args, **kwargs)
    except Unparsable: return None

# Some often-used actions:
def hug(*xs): return xs
def join(*strs): return ''.join(strs)

# A raw-access action:
def position(rules, text, utmost, st):
    return State(st.pos, st.vals + (st.pos,))
