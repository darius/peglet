# Adapted from http://hepunx.rl.ac.uk/~adye/jsspec11/llr.htm

from peglet import Parser

# XXX this line is reflected from (I think) the original:
#           ShiftExpression RelationalOperator RelationalExpression
# XXX what about &=, etc?

grammar = r"""
Program = _ Elements $

Elements =
          Element Elements
        | 
Element = 
          function\b _ Identifier \( _ ParameterListOpt \) _ CompoundStatement
        | Statement

ParameterListOpt = ParameterList | 
ParameterList = 
          Identifier , _ ParameterList
        | Identifier

CompoundStatement = 
          { _ Statements } _

Statements = 
          Statement Statements
        | 

Statement = 
          ; _
        | if\b _ Condition Statement else\b _ Statement
        | if\b _ Condition Statement
        | while\b _ Condition Statement
        | ForBegin in\b _ Expression \) _ Statement
        | ForBegin ; _ ExpressionOpt ; _ ExpressionOpt \) _ Statement
        | ForParen ; _ ExpressionOpt ; _ ExpressionOpt \) _ Statement
        | break\b _ ; _
        | continue\b _ ; _
        | with\b _ \( _ Expression \) _ Statement
        | return\b _ ExpressionOpt ; _
        | CompoundStatement
        | VariablesOrExpression ; _

Condition = 
          \( _ Expression \) _

ForParen = 
          for\b _ \( _

ForBegin = 
          ForParen VariablesOrExpression

VariablesOrExpression = 
          var\b _ Variables
        | Expression

Variables = 
          Variable , _ Variables
        | Variable

Variable = 
          Identifier [=] _ AssignmentExpression
        | Identifier

ExpressionOpt = 
          Expression
        | 

Expression = 
          AssignmentExpression , _ Expression
        | AssignmentExpression

AssignmentExpression = 
          ConditionalExpression AssignmentOperator AssignmentExpression
        | ConditionalExpression

ConditionalExpression = 
          OrExpression [?] _ AssignmentExpression : _ AssignmentExpression
        | OrExpression

OrExpression = 
          AndExpression [|][|] _ OrExpression
        | AndExpression

AndExpression = 
          BitwiseOrExpression && _ AndExpression
        | BitwiseOrExpression

BitwiseOrExpression = 
          BitwiseXorExpression [|] _ BitwiseOrExpression
        | BitwiseXorExpression

BitwiseXorExpression = 
          BitwiseAndExpression ^ _ BitwiseXorExpression
        | BitwiseAndExpression

BitwiseAndExpression = 
          EqualityExpression & _ BitwiseAndExpression
        | EqualityExpression

EqualityExpression = 
          RelationalExpression EqualityOperator EqualityExpression
        | RelationalExpression

RelationalExpression = 
          ShiftExpression RelationalOperator RelationalExpression
        | ShiftExpression

ShiftExpression = 
          AdditiveExpression ShiftOperator ShiftExpression
        | AdditiveExpression

AdditiveExpression = 
          MultiplicativeExpression [+] _ AdditiveExpression
        | MultiplicativeExpression - _ AdditiveExpression
        | MultiplicativeExpression

MultiplicativeExpression = 
          UnaryExpression MultiplicativeOperator MultiplicativeExpression
        | UnaryExpression

UnaryExpression = 
          UnaryOperator UnaryExpression
        | - _ UnaryExpression
        | IncrementOperator MemberExpression
        | MemberExpression IncrementOperator
        | MemberExpression
        | new\b _ Constructor
        | delete\b _ MemberExpression

Constructor = 
          this\b _ [.] _ ConstructorCall
        | ConstructorCall

ConstructorCall = 
          Identifier \( _ ArgumentListOpt \) _
        | Identifier [.] _ ConstructorCall
        | Identifier

MemberExpression = 
          PrimaryExpression [.] _ MemberExpression
        | PrimaryExpression \[ _ Expression \] _
        | PrimaryExpression \( _ ArgumentListOpt \) _
        | PrimaryExpression

ArgumentListOpt = 
          ArgumentList
        | 

ArgumentList = 
          AssignmentExpression , _ ArgumentList
        | AssignmentExpression

PrimaryExpression = 
          \( _ Expression \) _
        | { _ JsonPairs } _
        | { _ } _
        | Identifier
        | IntegerLiteral
        | FloatingPointLiteral
        | StringLiteral
        | false\b _
        | true\b _
        | null\b _
        | this\b _

JsonPairs = JsonPair , _ JsonPairs | JsonPair
JsonPair = JsonProperty : _ Expression
JsonProperty = Identifier | StringLiteral

AssignmentOperator     = [-+*/%]?= _ | &&= _ | ||= _
EqualityOperator       = [!=]=
RelationalOperator     = [<>]=?
ShiftOperator          = /XXX
MultiplicativeOperator = [*/%]
UnaryOperator          = /XXX
IncrementOperator      = [+][+] _ | -- _

Identifier = !Keyword ([A-Za-z_]\w*\b) _
Keyword    = (?:break|continue|delete|else|false|for|function|if|in|new|null|return|this|true|var|with|while)\b

IntegerLiteral = /XXX

FloatingPointLiteral = /XXX

StringLiteral = /XXX

_          = (?:\s|//[^\n]*\n?)*
"""

p = Parser(grammar)

eg = r"""
// Successfully advance a peg's parse rightwards.
function advance(maxP, p, value) {
    maxP.p = Math.max(maxP.p, p);
    return {p: p, value: value};
}
"""

## p(eg)
#. Traceback (most recent call last):
#.   File "/home/darius/git/peglet/peglet.py", line 48, in <lambda>
#.     return lambda text, rule=parts[1]: _parse(rules, actions, rule, text)
#.   File "/home/darius/git/peglet/peglet.py", line 102, in _parse
#.     else: raise Unparsable(rule, text[:utmost[0]], text[utmost[0]:])
#. Unparsable: ('Program', "\n// Successfully advance a peg's parse rightwards.\nfunction advance(maxP, p, value) {\n    maxP.p = Math.max(maxP.p, p);\n    return {p: p, value", ': value};\n}\n')
