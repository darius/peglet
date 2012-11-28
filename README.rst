peglet
======

Three goals:

1. A parsing library that's pleasant enough to use;

2. that's simple to adapt or rewrite from scratch if I'm faced with
   some new situation like a new programming language;

3. that inexpert programmers can follow without too much pain. 

So I aimed for one page of clear code not using combinators. Some bits
that couldn't fit those constraints (mainly #3) overflowed into a
combinator library, `parson <https://github.com/darius/parson>`_.

See https://github.com/darius/sketchbook/tree/master/parsing
for some early sketches.

See http://www.udacity.com/wiki/CS212%20Unit%203%20Code?course=cs212#grammarpy
and http://www.inf.puc-rio.br/~roberto/lpeg/ for some influences.

Thanks to Kragen Sitaker for ideas about the syntax.
