# Adapted from http://hepunx.rl.ac.uk/~adye/jsspec11/llr.htm

from peglet import Parser, hug, join

def maker(label):
    return lambda *parts: '(%s %s)' % (label, ' '.join(parts))

# XXX this line is reflected from (I think) the original:
#           ShiftExpression RelationalOperator RelationalExpression
# XXX what about &=, etc?
# XXX jsonPair: what level of Expression to use?

grammar = r"""
Program = _ Elements $

Elements =
          Element Elements
        | 
Element = 
          function\b _ Identifier \( _ ParameterListOpt \) _ CompoundStatement   mk_function
        | Statement

ParameterListOpt = ParameterList hug | hug
ParameterList = 
          Identifier , _ ParameterList
        | Identifier

CompoundStatement = 
          { _ Statements } _   mk_compound_statement
Statements = 
          Statement Statements
        | 

Statement = 
          ; _                                                          mk_empty_stmt
        | if\b _ Condition Statement else\b _ Statement                mk_if_else
        | if\b _ Condition Statement                                   mk_if
        | while\b _ Condition Statement                                mk_while
        | ForBegin in\b _ Expression \) _ Statement                    mk_for_in
        | ForBegin ; _ ExpressionOpt ; _ ExpressionOpt \) _ Statement  mk_for
        | ForParen ; _ ExpressionOpt ; _ ExpressionOpt \) _ Statement  mk_for
        | break\b _ ; _                                                mk_break
        | continue\b _ ; _                                             mk_coninue
        | with\b _ \( _ Expression \) _ Statement                      mk_with
        | return\b _ ExpressionOpt ; _                                 mk_return
        | CompoundStatement
        | VariablesOrExpression ; _

Condition = 
          \( _ Expression \) _

ForParen = 
          for\b _ \( _

ForBegin = 
          ForParen VariablesOrExpression

VariablesOrExpression = 
          var\b _ Variables   mk_var
        | Expression

Variables = 
          Variable , _ Variables
        | Variable
Variable = 
          Identifier [=] _ AssignmentExpression   mk_var_assign
        | Identifier

ExpressionOpt = 
          Expression
        | 

Expression = 
          AssignmentExpression , _ Expression   mk_comma_expression
        | AssignmentExpression

AssignmentExpression = 
          ConditionalExpression AssignmentOperator AssignmentExpression   mk_assign
        | ConditionalExpression

ConditionalExpression = 
          OrExpression [?] _ AssignmentExpression : _ AssignmentExpression   mk_conditional
        | OrExpression

OrExpression = 
          AndExpression [|][|] _ OrExpression   mk_oror
        | AndExpression

AndExpression = 
          BitwiseOrExpression && _ AndExpression   mk_andand
        | BitwiseOrExpression

BitwiseOrExpression = 
          BitwiseXorExpression ([|]) _ BitwiseOrExpression   mk_binop1
        | BitwiseXorExpression

BitwiseXorExpression = 
          BitwiseAndExpression (\^) _ BitwiseXorExpression   mk_binop2
        | BitwiseAndExpression

BitwiseAndExpression = 
          EqualityExpression (&) _ BitwiseAndExpression   mk_binop3
        | EqualityExpression

EqualityExpression = 
          RelationalExpression EqualityOperator EqualityExpression   mk_binop4
        | RelationalExpression

RelationalExpression = 
          ShiftExpression RelationalOperator RelationalExpression   mk_binop5
        | ShiftExpression

ShiftExpression = 
          AdditiveExpression ShiftOperator ShiftExpression   mk_binop6
        | AdditiveExpression

AdditiveExpression = 
          MultiplicativeExpression ([+-]) _ AdditiveExpression   mk_binop7
        | MultiplicativeExpression

MultiplicativeExpression = 
          UnaryExpression MultiplicativeOperator MultiplicativeExpression   mk_binop8
        | UnaryExpression

UnaryExpression = 
          UnaryOperator UnaryExpression        mk_unop
        | (-) _ UnaryExpression                mk_unop
        | IncrementOperator MemberExpression   mk_preincr
        | MemberExpression IncrementOperator   mk_postincr
        | MemberExpression
        | new\b _ Constructor                  mk_new
        | delete\b _ MemberExpression          mk_delete

Constructor = 
          this\b _ [.] _ ConstructorCall   mk_this_call
        | ConstructorCall

ConstructorCall = 
          Identifier \( _ ArgumentListOpt \) _   mk_call
        | Identifier [.] _ ConstructorCall       mk_dot_call
        | Identifier

MemberExpression = 
          PrimaryExpression [.] _ MemberExpression      mk_dot
        | PrimaryExpression \[ _ Expression \] _        mk_sub
        | PrimaryExpression \( _ ArgumentListOpt \) _   mk_call
        | PrimaryExpression

ArgumentListOpt = ArgumentList hug | hug
ArgumentList = 
          AssignmentExpression , _ ArgumentList
        | AssignmentExpression

PrimaryExpression = 
          \( _ Expression \) _
        | { _ JsonPairs } _      mk_object
        | { _ } _                mk_object
        | array                  mk_array
        | Identifier             mk_varref
        | FloatingPointLiteral   mk_float
        | IntegerLiteral         mk_float
        | StringLiteral          mk_string
        | false\b _              mk_literal
        | true\b _               mk_literal
        | null\b _               mk_literal
        | this\b _               mk_this

JsonPairs = JsonPair , _ JsonPairs | JsonPair
JsonPair = JsonProperty : _ AssignmentExpression   hug
JsonProperty = Identifier | StringLiteral

array    = \[ _ elements \] _
         | \[ _ \] _
elements = AssignmentExpression , _ elements
         | AssignmentExpression

AssignmentOperator     = ([-+*/%&^|]?=) _ | (<<=) | (>>>?=) | (&&=) _ | ([|][|]=) _
EqualityOperator       = ([!=]==?) _
RelationalOperator     = ([<>]=?) _
ShiftOperator          = (<<) _ | (>>>?) _
MultiplicativeOperator = ([*/%]) _
UnaryOperator          = ([+~!]) _
IncrementOperator      = ([+][+]) _ | (--) _

Identifier = !Keyword ([A-Za-z_]\w*) _
Keyword    = (?:break|continue|delete|else|false|for|function|if|in|new|null|return|this|true|var|with|while)\b

IntegerLiteral = int            join
FloatingPointLiteral = number   join

number   = int frac exp _
         | int frac _
         | int exp _
         | int _

int      = (-[1-9]) digits
         | (-) digit
         | ([1-9]) digits
         | digit
frac     = ([.]) digits
exp      = ([eE][+-]?) digits
digits   = (\d+)
digit    = (\d)

StringLiteral = string
string   = " chars " _            join
         | ' sqchars ' _          join
chars    = char chars |
char     = ([^\x00-\x1f"\\]) | esc_char
sqchars  = sqchar sqchars |
sqchar   = ([^\x00-\x1f'\\]) | esc_char

esc_char = \\(['"/\\])
         | \\([bfnrt])            escape
         | \\u xd xd xd xd   join u_escape
xd       = ([0-9a-fA-F])

_          = (?:\s|//[^\n]*\n?)*
"""

p = Parser(grammar,
           hug = lambda *xs: '[%s]' % ' '.join(xs),
           join = join,
           mk_array = maker('array'),
           mk_assign = maker('assign'),
#           mk_binop = lambda *vals: repr(vals),   #maker('binop'),
           mk_binop1 = maker('binop1'),
           mk_binop2 = maker('binop2'),
           mk_binop3 = maker('binop3'),
           mk_binop4 = maker('binop4'),
           mk_binop5 = maker('binop5'),
           mk_binop6 = maker('binop6'),
           mk_binop7 = maker('binop7'),
           mk_binop8 = maker('binop8'),
           mk_call = maker('call'),
           mk_comma_expression = maker('comma_expression'),
           mk_compound_statement = maker('compound_statement'),
           mk_dot = maker('dot'),
           mk_float = maker('float'),
           mk_function = maker('function'),
           mk_if = maker('if'),
           mk_new = maker('new'),
           mk_object = maker('object'),
           mk_return = maker('return'),
           mk_string = maker('string'),
           mk_unop = maker('unop'),
           mk_var = maker('var'),
           mk_var_assign = maker('var_assign'),
           mk_varref = maker('_'),
           )

eg = r"""
// Successfully advance a peg's parse rightwards.
function advance(maxP, p, value) {
    maxP.p = Math.max(maxP.p, p);
    return {p: p, value: value};
}
"""

## p(eg)
#. ('(function advance [maxP p value] (compound_statement (assign (dot (_ maxP) (_ p)) = (dot (_ Math) (call (_ max) [(dot (_ maxP) (_ p)) (_ p)]))) (return (object [p (_ p)] [value (_ value)]))))',)

hm = r"""
{p: p };
"""
## p(hm)
#. ('(object [p (_ p)])',)

eg2 = r"""function parseAll(peg, input) {
    var maxP = {p: 0};
    var r = pegSequence([peg, pegEndOfInput])(input, maxP, 0);
    if (!r) throw new Error("Bad syntax: "
                            + input.slice(0, maxP.p) + '>><<'
                            + input.slice(maxP.p));
    return r.value;
}
"""

## p(eg2)
#. Traceback (most recent call last):
#.   File "/home/darius/git/peglet/peglet.py", line 59, in <lambda>
#.     return lambda text, rule=parts[1]: _parse(rules, actions, rule, text)
#.   File "/home/darius/git/peglet/peglet.py", line 113, in _parse
#.     else: raise Unparsable(rule, text[:far], text[far:])
#. Unparsable: ('Program', 'function parseAll(peg, input) {\n    var maxP = {p: 0};\n    var r = pegSequence([peg, pegEndOfInput])', '(input, maxP, 0);\n    if (!r) throw new Error("Bad syntax: "\n                            + input.slice(0, maxP.p) + \'>><<\'\n                            + input.slice(maxP.p));\n    return r.value;\n}\n')
