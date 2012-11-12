import collections, re
# from itertools import count

def Parser(grammar, **actions):
    # Map the name of each grammar rule to a list of its alternatives.
    rules = collections.defaultdict(list)
    lines = [line for line in grammar.splitlines() if line.strip()]
    for line in lines:
        tokens = line.split()
        if tokens: rules[tokens[0]].append(tokens[1:])

    def comp():
        for rule, alternatives in rules.items():
            for line in comp_rule(rule, alternatives):
                yield line

    def comp_rule(rule, alternatives):
        yield "def %s(text, far, i):" % rule
        for a, alternative in enumerate(alternatives):
            yield '    def alt_%s(text, far, i):' % a
            yield '        vals = ()'
            yield '        st = i, vals'
            for line in comp_alternative(alternative):
                yield '        ' + line
        yield ('    return '
               + ' or '.join('alt_%d(text, far, i)' % a
                             for a, _ in enumerate(alternatives)))

    def comp_alternative(alternative):
        for token in alternative:
            yield 'i, vals = st'
            for line in comp_token(token):
                yield line
            yield 'if st is None: return None'
        yield 'return st'

    def comp_token(token):
        if token.startswith('::'):
            yield 'st = %s({}, text, far, st)' % token[2:]
        elif token.startswith(':'):
            yield 'st = (i, (%s(*vals),))' % token[1:]
        elif token.startswith('!'):
            assert False, "TBD"
        elif token in rules:
            yield 'st = %s(text, far, st)' % token
        else:
            yield 'm = re.match(%r, text[i:])' % token
            yield 'if not m: return None'
            yield 'i += m.end()'
            yield 'far[0] = max(far[0], i)'
            yield 'vals += m.groups()'
            yield 'st = i, vals'

## exec(nums_grammar)
## num('42', [0], 0)
#. (2, (42,))
#  (2, (42,))

## print nums_grammar
#. def num(text, far, i):
#.     def alt_0(text, far, i):
#.         vals = ()
#.         st = i, vals
#.         i, vals = st
#.         m = re.match('([0-9]+)', text[i:])
#.         if not m: return None
#.         i += m.end()
#.         far[0] = max(far[0], i)
#.         vals += m.groups()
#.         st = i, vals
#.         if st is None: return None
#.         i, vals = st
#.         st = (i, (int(*vals),))
#.         if st is None: return None
#.         return st
#.     return alt_0(text, far, i)
#. def allnums(text, far, i):
#.     def alt_0(text, far, i):
#.         vals = ()
#.         st = i, vals
#.         i, vals = st
#.         st = nums(text, far, st)
#.         if st is None: return None
#.         i, vals = st
#.         m = re.match('$', text[i:])
#.         if not m: return None
#.         i += m.end()
#.         far[0] = max(far[0], i)
#.         vals += m.groups()
#.         st = i, vals
#.         if st is None: return None
#.         return st
#.     return alt_0(text, far, i)
#. def nums(text, far, i):
#.     def alt_0(text, far, i):
#.         vals = ()
#.         st = i, vals
#.         i, vals = st
#.         st = num(text, far, st)
#.         if st is None: return None
#.         i, vals = st
#.         m = re.match(',', text[i:])
#.         if not m: return None
#.         i += m.end()
#.         far[0] = max(far[0], i)
#.         vals += m.groups()
#.         st = i, vals
#.         if st is None: return None
#.         i, vals = st
#.         st = nums(text, far, st)
#.         if st is None: return None
#.         return st
#.     def alt_1(text, far, i):
#.         vals = ()
#.         st = i, vals
#.         i, vals = st
#.         st = num(text, far, st)
#.         if st is None: return None
#.         return st
#.     def alt_2(text, far, i):
#.         vals = ()
#.         st = i, vals
#.         return st
#.     return alt_0(text, far, i) or alt_1(text, far, i) or alt_2(text, far, i)
#. 



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

    return '\n'.join(comp())

nums_grammar = Parser(r"""
allnums   nums $

nums   num , nums
nums   num
nums   

num    ([0-9]+) :int
""")

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
