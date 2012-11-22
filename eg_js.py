# Adapted from http://hepunx.rl.ac.uk/~adye/jsspec11/llr.htm

from peglet import Parser

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
        | array
        | Identifier
        | FloatingPointLiteral
        | IntegerLiteral
        | StringLiteral
        | false\b _
        | true\b _
        | null\b _
        | this\b _

JsonPairs = JsonPair , _ JsonPairs | JsonPair
JsonPair = JsonProperty : _ AssignmentExpression
JsonProperty = Identifier | StringLiteral

array    = \[ _ elements \] _     mk_array
         | \[ _ \] _              mk_array
elements = AssignmentExpression , _ elements
         | AssignmentExpression

AssignmentOperator     = [-+*/%&^|]?= _ | <<= | >>>?= | &&= _ | ||= _
EqualityOperator       = [!=]==? _
RelationalOperator     = [<>]=? _
ShiftOperator          = << | >>>?
MultiplicativeOperator = [*/%] _
UnaryOperator          = [+~!] _
IncrementOperator      = [+][+] _ | -- _

Identifier = !Keyword ([A-Za-z_]\w*\b) _
Keyword    = (?:break|continue|delete|else|false|for|function|if|in|new|null|return|this|true|var|with|while)\b

IntegerLiteral = int            join mk_number
FloatingPointLiteral = number   join mk_number

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
chars    = char chars
         |
char     = ([^\x00-\x1f"\\])
         | \\(["/\\])
         | \\([bfnrt])            escape
         | \\u xd xd xd xd   join u_escape
xd       = ([0-9a-fA-F])

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
#. ('advance', 'maxP', 'p', 'value', 'maxP', 'p', 'Math', 'max', 'maxP', 'p', 'p', 'p', 'p', 'value', 'value')

hm = r"""
{p: p };
"""
## p(hm)
#. ('p', 'p')
