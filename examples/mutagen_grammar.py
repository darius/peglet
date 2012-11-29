"""
Parse Mutagen grammars from a hopefull human-friendly format.
Then have them generate random text.
"""

from peglet import Parser, hug, join

from mutagen import mutagen, empty, abut, capitalize, a_an, delay, \
    literal, sequence, weighted_choice, fixed, shuffled, separator, terminator

def mk_punct(s):
    return {'.': terminator('.'),
            '?': terminator('?'),
            '!': terminator('!'),
            ',': separator(','),
            ';': separator(';'),
            '-': sequence(abut, literal('-'), abut),
            '--': literal('--')}[s]

def parse(grammar):

    rules = {'-a-': a_an,
             '-an-': a_an,
             '-a-an-': a_an,
             '-adjoining-': abut,
             '-capitalize-': capitalize}

    parser = Parser(r"""
grammar = _ rules
rules   = rule rules | 

rule    = name [=] _ exp       hug

exp     = alts                 mk_choice
alts    = alt [/] _ alts
        | alt
alt     = \[ number \] _ seq   mk_weight
        | seq                  mk_unit
seq     = factor seq           mk_seq
        |                      mk_empty
factor  = name ![=]            mk_ref
        | punct                mk_punct
        | \( _ exp \) _
        | { _ alts } _         mk_shuffle
        | word { _ alts } _    mk_fixed
        | word                 mk_literal
punct   = ([.,;?!]) _
        | (--?)\s _
word    = ([A-Za-z0-9']+) _

name    = (-[A-Za-z0-9'-]+-) _
number  = (\d+) _              int
_       = (?:\s|#.*\n?)*
""", 
               hug=hug,
               int=int,
               mk_choice  = lambda *pairs: pairs[0][0] if 1 == len(pairs) else weighted_choice(dict(pairs)),
               mk_empty   = lambda: empty,
               mk_fixed   = lambda tag, *pairs: fixed(tag)(dict(pairs)),
               mk_literal = literal,
               mk_punct   = mk_punct,
               mk_ref     = lambda name: delay(lambda: rules[name]),
               mk_seq     = lambda p, q: sequence(p, q) if q is not empty else p,
               mk_shuffle = lambda *pairs: shuffled(dict(pairs)),
               mk_unit    = lambda p: (p, 1),
               mk_weight  = lambda w, p: (p, w),
               )
    rules.update(parser(grammar))
    return rules

eg = """
# Translated from http://www.eblong.com/zarf/mutagen/goreyfate.js
#   GoreyFate: a Mutagen example.
#   Written by Andrew Plotkin <erkyrath@eblong.com>
#   This Javascript code is copyright 2009 by Andrew Plotkin. You may
#   copy, distribute, and modify it freely, by any means and under any
#   conditions.

-person-description- = -name-
    ([2] -comma-description-phrase- / [1] )

-name-   = gender{-male-name- / -female-name-}
-he-she- = gender{he / she}

-female-name- = Emmalissa / Chloe / Tiffani / Eunice / Zoe /
    Jennifer / Imelda / Yvette / Melantha
-male-name- = Bernard / Joseph / Emmett / Ogden / Eugene /
    Xerxes / Joshua / Lemuel / Etienne

-comma-description-phrase- = , -a-an- ([1] -person-adjective- / [1] )
    -descriptor-
    ([1] -descriptor-modifier- / [2] )
    ,

-person-adjective- = precocious / unflappable / energetic /
    forceful / inimitable / daring / mild / intense / jaded

-intensifier- = great / some / considerable / not inconsiderable /
    distinct / impressive / unique / notable

-descriptor- = [1] -neutral-descriptor-
    / [1] gender{-male-descriptor- / -female-descriptor-}
-neutral-descriptor- = toddler / aesthete / writer / artist
-male-descriptor- = stalwart / gentleman / boy / youth
-female-descriptor- = young miss / girl / maiden / flapper

-descriptor-modifier- = of -intensifier-
    (perspicacity / fortitude / passion / wit / 
        perception / presence of mind)
"""
rules = parse(eg)
## mutagen(rules['-person-description-'], 142)
#. 'Joseph, a stalwart,'
