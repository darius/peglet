"""
Parse Mutagen grammars from a hopefully human-friendly format.
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

-root- = -capitalize- -gorey-fate- .
-gorey-fate- = [2] -person-description- -action- -time- / [2] -time- -time-comma- -person-description- -action- / [1] (it was) -time- that -person-description- -action-
-action- = -passive-action- / -active-action-
-active-action- = -active-action-word- -active-action-prep- -a-an- ([1] -target-air- / [2] ()) ([1] -target-age- / [2] ()) -active-action-target-
-target-age- = old / moldering / aged / antiquated
-target-air- = disreputable / peculiar / mysterious / banal
-active-action-target- = altitude{ -active-action-target-hi- / -active-action-target-lo- }
-active-action-target-lo- = well / hole / cave / oubliette / cellar / pit
-active-action-target-hi- = tower / cliff / ruin / pillar / treehouse / garret
-active-action-prep- = altitude{ -active-action-prep-hi- / -active-action-prep-lo- }
-active-action-prep-lo- = down / into
-active-action-prep-hi- = down from / off / from
-active-action-word- = fell / tumbled / disappeared / plummeted / vanished / dropped
-passive-action- = -passive-action-word- ([2] -passive-action-qualifier- / [3] ())
-passive-action-qualifier- = away / at sea / without a trace / unexpectedly / mysteriously / into -action-result- / (away into) -action-result-
-action-result- = -dest-noun- / -dest-modifier- -dest-noun- / -a-an- -dest-noun- / -a-an- -dest-modifier- -dest-noun- / -a-an- -dest-form- of -dest-noun- / -a-an- -dest-form- of -dest-modifier- -dest-noun- / -a-an- -dest-modifier- -dest-form- of -dest-noun-
-dest-form- = solidity{ puddle / bucket / vat / heap / cloud / waft }
-dest-modifier- = noisome / pearlescent / foul / fetid / glittering / dark / briny / glistening / cloying
-dest-noun- = solidity{ slime / stew / secretion / mist / smoke / dust / vapor }
-passive-action-word- = exploded / vaporized / melted / sublimated / evaporated / transformed / calcified / vanished / faded / disappeared / shrivelled / bloated / liquefied / was lost / was misplaced / was bartered
-time-comma- = longtime{ -maybe-comma- / , / -maybe-comma- / -maybe-comma- / -maybe-comma- / -maybe-comma- / -maybe-comma- / , }
-maybe-comma- = [2] () / [1] ,
-time- = longtime{ one -day-weather- -day-part- / one -day-weather- -day-part- last -time-unit- / last -day-of-week- / last -time-unit- / -a-an- -time-unit- ago / on -holiday- / last -holiday- / -a-an- -time-unit- ago -holiday- / -two-to-six- -time-unit- -adjoining- s ago / -travel-time- }
-travel-time- = ([2] while / [1] whilst) (on safari to / exploring / on an expedition to / hunting in / on sabbatical in) -travel-place-
-travel-place- = Mozambique / Uganda / the Seychelles / the Vatican / Peoria / Borneo / Antarctica / Somerville / Northumberland / Saxony / Brugges / Gondwanaland
-holiday- = Christmas / Boxing Day / St. Swithin's Day
-day-of-week- = Monday / Tuesday / Wednesday / Thursday / Friday / Saturday
-day-part- = day / afternoon / morning / evening
-time-unit- = week / month / season
-day-weather- = [1] rainy / foggy / blistering / blustery / gloomy / dank / [2] ()
-two-to-six- = two / three / four / five / six / some
-person-description- = -name- ([2] -comma-description-phrase- / [1] ())
-comma-description-phrase- = , -a-an- ([1] -person-adjective- / [1] ()) -descriptor- ([1] -descriptor-modifier- / [2] ()) ,
-descriptor-modifier- = of -intensifier- (perspicacity / fortitude / passion / wit / perception / presence of mind)
-descriptor- = [1] -neutral-descriptor- / [1] gender{ -male-descriptor- / -female-descriptor- }
-female-descriptor- = young miss / girl / maiden / flapper
-male-descriptor- = stalwart / gentleman / boy / youth
-neutral-descriptor- = toddler / aesthete / writer / artist
-intensifier- = great / some / considerable / not inconsiderable / distinct / impressive / unique / notable
-person-adjective- = precocious / unflappable / energetic / forceful / inimitable / daring / mild / intense / jaded
-he-she- = gender{ he / she }
-name- = gender{ -male-name- / -female-name- }
-male-name- = Bernard / Joseph / Emmett / Ogden / Eugene / Xerxes / Joshua / Lemuel / Etienne
-female-name- = Emmalissa / Chloe / Tiffani / Eunice / Zoe / Jennifer / Imelda / Yvette / Melantha
"""
rules = parse(eg)
## mutagen(rules['-root-'], 0)
#. 'It was five months ago that Etienne, a boy of some perspicacity, sublimated.'
