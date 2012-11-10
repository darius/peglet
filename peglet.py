import collections, re

# A parsing state: a position in the input text and a values tuple.
State = collections.namedtuple('State', 'pos vals'.split())

def Grammar(grammar, **actions):
    r"""Make a parsing function from a PEG grammar. You supply the
    grammar as a string with one line per alternative, like the
    example grammar below. Each line starts with the name of the rule
    it defines an alternative for; each following token is a regex, a
    rule name, or an action name. (Possibly preceded by '!' for
    negation: !foo successfully parses when foo *fails* to parse.)

    Results get added by regex captures and transformed by actions
    (which are named like ':wrap' below; to say what 'wrap' means
    here, make it a keyword argument).

    Actions named like '::action' get raw access to the parsing state.

    The parsing function maps a string a results tuple or raises
    Unparsable. (It can optionally take a rule name to start from, by
    default the first in the grammar.) It doesn't necessarily match
    the whole input, just a prefix.

    >>> parse_s_expression = Grammar(r'''
    ... one_expr   _ expr !.
    ... _          \s*
    ... expr       \( _ exprs \) _ :wrap
    ... expr       ([^()\s]+) _
    ... exprs      expr exprs
    ... exprs      ''',             wrap = lambda *vals: vals)
    >>> parse_s_expression('  (hi (john mccarthy) (()))')
    (('hi', ('john', 'mccarthy'), ((),)),)
    >>> parse_s_expression('(too) (many) (exprs)')
    Traceback (most recent call last):
    Unparsable: ('one_expr', ('(too) ', '(many) (exprs)'))
    """
    # Map the name of each grammar rule to a list of its alternatives.
    rules = collections.defaultdict(list)
    lines = [line for line in grammar.splitlines() if line.strip()]
    for line in lines:
        tokens = line.split()
        if tokens: rules[tokens[0]].append(tokens[1:])

    def parse(text, rule=lines[0].split()[0]):
        "Parse a prefix of text; return a results tuple or Unparsable."
        utmost = [0]
        st = parse_rule(rule, text, utmost, State(0, ()))
        if st: return st.vals
        else: raise Unparsable(rule, (text[:utmost[0]], text[utmost[0]:]))

    # Each parsing function starts from a state st and returns either
    # None (failure) or an updated state. We also track utmost: a
    # mutable box holding the rightmost position positively reached.

    def parse_rule(name, text, utmost, st):
        for alternative in rules[name]:
            st2 = parse_sequence(alternative, text, utmost, st)
            if st2: return st2
        return None

    def parse_sequence(tokens, text, utmost, st):
        for token in tokens:
            st = parse_token(token, text, utmost, st)
            if not st: break
        return st

    def parse_token(token, text, utmost, st):
        if token.startswith('::'):
            return actions[token[2:]](rules, text, utmost, st)
        elif token.startswith(':'):
            return State(st.pos, (actions[token[1:]](*st.vals),))
        elif token.startswith('!'):
            return None if parse_token(token[1:], text, [0], st) else st
        elif token in rules:
            st2 = parse_rule(token, text, utmost, State(st.pos, ()))
            return State(st2.pos, st.vals + st2.vals) if st2 else None
        else:
            m = re.match(token, text[st.pos:])
            if not m: return None
            utmost[0] = max(utmost[0], st.pos + m.end())
            return State(st.pos + m.end(), st.vals + m.groups())

    return parse

class Unparsable(Exception): pass

def maybe(parse, *args, **kwargs):
    try:
        return parse(*args, **kwargs)
    except Unparsable:
        return None

# Some often-used actions:
def chunk(*xs): return xs
def cat(*strs): return ''.join(strs)

# A raw-access action:
def position(rules, text, utmost, st):
    return State(st.pos, st.vals + (st.pos,))
