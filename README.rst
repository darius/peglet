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


Installing it
=============

Either ``pip install peglet`` or ``python setup.py install``.


Using it
========

Peglet extends Python's regular expressions to handle recursive
grammars. For example, to parse a tiny subset of HTML:

>>> from peglet import Parser
>>> a_little_html = Parser(r"""
... parts = part parts | 
... part  = <(\w+)> parts </\w+> group
...       | ([^<]+)
... """, group=lambda *values: values)
>>> a_little_html("Hello. <p><em>Nesting</em> for <i>the win</i>.</p>")
('Hello. ', ('p', ('em', 'Nesting'), ' for ', ('i', 'the win'), '.'))

See the module doc and the examples/ directory for more.
