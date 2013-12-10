"""
Like http://www.eblong.com/zarf/mutagen/mutagen.js
(More or less; assume 'less', for now.)
The C version of Elite would be another thing-of-this-sort to study.

This is here among the peglet examples just to interpret the outputs
of mutagen_grammar.py.

TODO:
  - better naming
  - documentation
  - compare to original and learn from the difference
"""

import bisect, collections, itertools, random

def mutagen(gen, seed=None):
    "Return a random-ish string chosen according to gen and seed."
    return render('', no_op, desugar(gen)(RNG(seed)))


# Grammar constructors
# gen: rng -> [insn]

def desugar(x):
    if isinstance(x, (unicode, str)):
        return literal(x)
    elif isinstance(x, tuple):
        return sequence(*x)
    elif callable(x):
        return x
    else:
        assert False, x

def empty(rng):      return []
def abut(rng):       return [abut_insn]
def capitalize(rng): return [capitalize_insn]
def a_an(rng):       return [a_an_insn]

def delay(thunk):
    return lambda rng: thunk()(rng)

def literal(s):
    return lambda rng: [lit_insn(s)]

def sequence(*gens):
    gens = map(desugar, gens)
    return lambda rng: sum([gen(rng) for gen in gens], [])

def choice(*gens):
    return weighted_choice(dict((gen, 1) for gen in gens))

def weighted_choice(pairs):
    return Chooser(pairs, lambda rng, n: rng.choose(n))
def fixed(tag):
    return lambda pairs: (
        Chooser(pairs, lambda rng, n: rng.choose_fixed(tag, n)))
def shuffled(pairs):
    tag = next(tags)
    return Chooser(pairs, lambda rng, n: rng.choose_shuffled(tag, n))

tags = itertools.count()

def Chooser(pairs, method):
    gens, weights = pairs.keys(), pairs.values()
    gens = map(desugar, gens)
    totals = []
    for w in weights:
        totals.append(w + totals[-1] if totals else w)
    def chooser(rng):
        i = bisect.bisect(totals, method(rng, totals[-1]))
        # Don't assume i is in range, because the grammar might have
        # inconsistent uses of a fix-tag (with different numbers of
        # choices or sums of weights).
        return gens[i % len(gens)](rng)
    return chooser

def separator(punctuation):
    return sequence(abut, literal(punctuation))

def terminator(punctuation):
    return sequence(abut, literal(punctuation), capitalize)

comma  = separator(",")
period = terminator(".")


# Choosing

class RNG:

    def __init__(self, seed=None):
        self.random = random.Random(seed)
        self.fixings = {}
        self.shufflings = collections.defaultdict(set)

    def choose(self, n):
        return self.random.randint(0, n-1)

    def choose_fixed(self, tag, n):
        try:
            return self.fixings[tag]
        except KeyError:
            result = self.fixings[tag] = self.choose(n)
            return result

    def choose_shuffled(self, tag, n):
        seen = self.shufflings[tag]
        if n <= len(seen): seen.clear()
        while True:
            result = self.choose(n)
            if result in seen: continue
            seen.add(result)
            return result


# Rendering
# insn: string, (string->string), [insn] -> string
# (Kind of inefficient; tightened up in the rendering.py version, but
# that code's harder to follow.)

def render(space, cap, insns):
    return insns[0](space, cap, insns[1:]) if insns else ''

def lit_insn(s):
    return lambda space, cap, insns: space + cap(s) + render(' ', no_op, insns)

def abut_insn(space, cap, insns):
    return render('', cap, insns)

def capitalize_insn(space, cap, insns):
    return render(space, str.capitalize, insns)

def a_an_insn(space, cap, insns):
    rest = render(' ', no_op, insns)
    return space + cap("an" if rest.lstrip().startswith(vowels) else "a") + rest

vowels = tuple('aeiouAEIOU')

no_op = lambda s: s


# Tests

def eg(gen): return mutagen(gen, 142)

## eg(("hello", empty, "world"))
#. 'hello world'

## eg(choice("hello", comma, "cruel", "world"))
#. ','

## eg((capitalize, "hello", comma, a_an, "cruel", "world", period, a_an, "ah", period))
#. 'Hello, a cruel world. An ah.'

## L = fixed(0)
## def yn(s): return L(dict((c, 1) for c in s.split()))
## eg((yn('0 1'), yn('N Y'), yn('F T')))
#. '0 N F'

wchoice = weighted_choice

by_gender = fixed('gender')

FemaleName = choice("Emmalissa", "Chloe", "Tiffani", "Eunice", "Zoe",
    "Jennifer", "Imelda", "Yvette", "Melantha")
MaleName = choice("Bernard", "Joseph", "Emmett", "Ogden", "Eugene",
    "Xerxes", "Joshua", "Lemuel", "Etienne")

Name = by_gender({MaleName: 1, FemaleName: 1})
HeShe = by_gender({"he": 1, "she": 1})

PersonAdjective = choice("precocious", "unflappable", "energetic",
    "forceful", "inimitable", "daring", "mild", "intense", "jaded")

Intensifier = choice("great", "some", "considerable", "not inconsiderable",
    "distinct", "impressive", "unique", "notable")

NeutralDescriptor = choice("toddler", "aesthete", "writer", "artist")
MaleDescriptor = choice("stalwart", "gentleman", "boy", "youth")
FemaleDescriptor = choice("young miss", "girl", "maiden", "flapper")
Descriptor = wchoice({NeutralDescriptor: 1,
                      by_gender({MaleDescriptor: 1, FemaleDescriptor: 1}): 1})

DescriptorModifier = ("of", Intensifier,
                      choice("perspicacity", "fortitude", "passion", "wit",
                             "perception", "presence of mind"))

CommaDescriptionPhrase = (comma, a_an,
                          wchoice({PersonAdjective: 1, empty: 1}),
                          Descriptor,
                          wchoice({DescriptorModifier: 1, empty: 2}),
                          comma)

PersonDescription = (Name,
                     wchoice({CommaDescriptionPhrase: 2, empty: 1}))

## eg(PersonDescription)
#. 'Emmett, a boy of great perspicacity,'
