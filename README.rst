Peglet
======

Peglet extends Python's regular expressions to handle recursive
grammars. For example, to parse a tiny subset of HTML:

>>> from peglet import Parser
>>> a_little_html = Parser(r"""
...     parts = part parts | 
...     part  = <(\w+)> parts </\w+> group
...           | ([^<]+)
... """, group=lambda *values: values)
>>> a_little_html("Hello. <p><em>Nesting</em> for <i>the win</i>.</p>")
('Hello. ', ('p', ('em', 'Nesting'), ' for ', ('i', 'the win'), '.'))

The goal was to make a parsing library

1. pleasant enough to use;

2. simple to adapt or rewrite from scratch if I'm faced with some new
   situation like a new programming language;

3. with code easy enough to follow that it could introduce people to
   parsing.

So it came down to one page of clear code not using combinators. (And
then ballooned to 200+ lines from documentation and a few extras.)
Some bits that couldn't fit the latter two constraints went into a
combinator library, `parson <https://github.com/darius/parson>`_.

For more, see `the examples
<https://github.com/darius/peglet/tree/master/examples>`_ or the
module doc in `the code
<https://github.com/darius/peglet/blob/master/peglet.py>`_.


Installing it
=============

``pip install peglet``, or else download then ``python setup.py install``.
