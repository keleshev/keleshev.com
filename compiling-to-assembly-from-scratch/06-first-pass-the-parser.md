---
title: "6. First Pass: The Parser • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 6</small></small><br/>First Pass: The Parser<br/><br/></h1>
```

\chapter{First Pass: The Parser}
\includegraphics{chapter-illustrations/6.png}
\newpage


Now that we've got enough parsing machinery working, we can implement the parser that produces an AST from source for our compiler.

## Whitespace and comments

First, let's define parsers for whitespace and comments, which we collectively refer to as *ignored*.
(When a parser is split into a lexer and a parser, parsing whitespace and comments is usually done at the lexer-level.)

```js
let whitespace = regexp(/[ \n\r\t]+/y);
let comments =
  regexp(/[/][/].*/y).or(regexp(/[/][*].*[*][/]/sy));
let ignored = zeroOrMore(whitespace.or(comments));
```

We allow both single-line (`// …`{.js}) and multi-line (`/* … */`{.js}) comments.
In JavaScript regular expressions, the dot matches any character, *except* newline.
To implement multi-line comments, we need to match newline as well.
It is possible to alter the meaning of the dot regular expression to match any character *including* newline by passing the "dot-all" flag "`s`" alongside the "sticky" flag "`y`":

```js
/[/][*].*[*][/]/sy
```

We use character classes with a single character like `[*]` as a readable way to escape characters that have special meaning in regular expressions.
Otherwise, they quickly start looking like a broken saw:

```js
/\/\*.*\*\//sy
```

## Tokens

Even though our parser is scanerless (or token-less), it is still useful to distinguish tokens as our syntactic building blocks.
The idea is to build token-like parsers from simple character parsers, and only then build full parser on top of token-like parsers.

As customary, we will use the naming convention for tokens (in grammar rules and parsers): they will be upper-case.

Tokens provide us a higher-level view of our source than single characters.
They allow us to not deal with minute details like whitespace and comments.
And this is precisely how we'll use them here.
We'll define a `token` parser combinator (or, more precisely, constructor) that allows us to ignore whitespace and comments around our lexemes (or tokens).

```js
let token = (pattern) =>
  regexp(pattern).bind((value) =>
    ignored.and(constant(value)));
```

It takes a regular expression pattern and returns a parser that is a sequence of that pattern and an `ignored` rule that we defined previously to handle whitespace and comments.
It produces the string value matched by the pattern but ignores the value of the `ignored` rule.
We "pad" with `ignored` only on the right-hand-side, not around the pattern.
The latter would be redundant in all but the first token, which we can handle specially.
This is a common way to handle whitespace and comments in scanerless parsers.

We'll start with defining tokens for keywords in our language, like `function`{.js}, `if`{.js}, `else`{.js}, `return`{.js}, `var`{.js}, and `while`{.js}:

```js
let FUNCTION = token(/function\b/y);
let IF = token(/if\b/y);
let ELSE = token(/else\b/y);
let RETURN = token(/return\b/y);
let VAR = token(/var\b/y);
let WHILE = token(/while\b/y);
```

We've used a word-break escape sequence `\b` to make sure we don't recognize `functional` as a keyword `function`{.js} followed by identifier `al`.

Then, tokens for punctuation: commas, parenthesis, etc.:

```js
let COMMA = token(/[,]/y);
let SEMICOLON = token(/;/y);
let LEFT_PAREN = token(/[(]/y);
let RIGHT_PAREN = token(/[)]/y);
let LEFT_BRACE = token(/[{]/y);
let RIGHT_BRACE = token(/[}]/y);
```

Our baseline compiler will handle only decimal integer numbers *(base 10)*:

\newpage

```js
let NUMBER =
  token(/[0-9]+/y).map((digits) =>
    new Number(parseInt(digits, 10)));
```

We map the `[0-9]+` token to convert digits to a JavaScript number using `parseInt` JavaScript built-in function that takes a string and a base number (10 for decimal).
Then we construct a `Number` AST node from it.

Identifiers start with a letter or an underscore and are followed by a number of letters, digits, and underscores.
In other words, they can't start with a digit.

```js
let ID = token(/[a-zA-Z_][a-zA-Z0-9_]*/y);
```

In some cases, it will be useful for us to parse identifiers just for their string value, but sometimes it is more convenient to produce the AST node.
That's why we create an alias `id`, which is the same as `ID`, but instead of producing a string, it produces an AST node `Id`.

```js
let id = ID.map((x) => new Id(x));
```

Now, the operator tokens:

```js
let NOT = token(/!/y).map((_) => Not);
let EQUAL = token(/==/y).map((_) => Equal);
let NOT_EQUAL = token(/!=/y).map((_) => NotEqual);
let PLUS = token(/[+]/y).map((_) => Add);
let MINUS = token(/[-]/y).map((_) => Subtract);
let STAR = token(/[*]/y).map((_) => Multiply);
let SLASH = token(/[/]/y).map((_) => Divide);
let ASSIGN = token(/=/y).map((_) => Assign);
```

We cannot construct a full AST node out of a single operator, but it will be handy to return the class of the AST node.

## Grammar

The grammar for our baseline compiler is split into two parts: *expressions* and *statements*.
JavaScript (and TypeScript) is pretty relaxed about distinguishing the two.
In general, expressions are constructs that produce a value like `1 + 2`, and statements are something that has an effect but does not produce a value, like a `while` loop.

## Expression parser

We will start by constructing a parser for a single expression.
Here is the grammar for an expression in the baseline language.

```
args <- (expression (COMMA expression)*)?
call <- ID LEFT_PAREN args RIGHT_PAREN
atom <- call / ID / NUMBER
      / LEFT_PAREN expression RIGHT_PAREN
unary <- NOT? atom
product <- unary ((STAR / SLASH) unary)*
sum <- product ((PLUS / MINUS) product)*
comparison <- sum ((EQUAL / NOT_EQUAL) sum)*
expression <- comparison
```

It consists of infix operations such as `==`, `!=`, `+`, `-`, `*`, `/`, unary negation `!x`, identifiers, integer numbers, and function calls.

The expression rule is split into several layers in order to handle operator precedence.
The `expression` itself is just an alias to `comparison`.
The `comparison` rule represents the operators with the lowest precedence: `==` and `!=`.
The `comparison` itself is built out of `sum` in which operators have higher precedence: `+` and `-`.
The `sum`, in turn, is built out of `product` rules with the highest precedence among infix operators: `*` and `/`.
Those are built from `unary`, which represents unary operators, of which we have only negation: `!`.
Negation has the highest precedence among all our operators.
It is built upon a rule called `atom`.
The `atom` rule represents the rules that are "atomic", or require no precedence because of the way they are structured.
For example, `ID` and `NUMBER` are single lexemes, so precedence doesn't apply, while `call` and parenthesized expressions have explicit delimiters, so precedence doesn't apply either.
The `args` rule is extracted to simplify the `call` rule.

This process of constructing parsers with increasing precedence is sometimes compared to adding beads to a rope.

You can probably notice that the lowest-level rules, such as `atom` and `call` (via `args`) refer back to `expression`.
This means that our grammar is *recursive*.
This creates a slight problem for constructing a parser for this grammar.
While JavaScript allows for recursive functions, it does not allow for recursive values.
Other languages allow for so-called `let-rec` bindings, but not JavaScript.
The way we handle this is by initially defining `expression` as an `error` parser:

```js
let expression: Parser<AST> =
  Parser.error(
    "Expression parser used before definition");
```

Now we are free to use it when constructing our parser.
However, we must remember to change this parser in-place once we define `comparison` and before we use it:

```js
expression.parse = comparison.parse;
```

## Call parser

We need to implement `call` by first implementing `args`.

```	
args <- (expression (COMMA expression)*)?
call <- ID LEFT_PAREN args RIGHT_PAREN
```

Mechanically converting the `args` to a parser gives us:

```js
// args <- (expression (COMMA expression)*)?
let args =
  maybe(
    expression.and(zeroOrMore(COMMA.and(expression))))
```

Like in the case of the `Call` AST node, we called it `args` instead of `arguments`, because `arguments` is a special JavaScript object, and we don't want to clash with it.

We want this parser to return something useful, like an array of AST nodes.
The `maybe` combinator returns `null` if it doesn't match, but we want an empty array, so let's replace it with `.or(constant([]))`.
We need to bind the first expression, then the rest of the expressions, and then concatenate them.
By doing that we end up with the following:

```js
// args <- (expression (COMMA expression)*)?
let args: Parser<Array<AST>> =
  expression.bind((arg) =>
    zeroOrMore(COMMA.and(expression)).bind((args) =>
      constant([arg, ...args]))).or(constant([]))
```

The expression `zeroOrMore(COMMA.and(expression))` conveniently ignores the commas and produces an array of AST nodes.

Now, implementing `call` mechanically from grammar gives us:

```js
// call <- ID LEFT_PAREN args RIGHT_PAREN
let call =
  ID.and(LEFT_PAREN.and(args.and(RIGHT_PAREN)))
```

We bind `ID` (that represents the name of the callee) and `args` to construct a `Call` node:

```js
// call <- ID LEFT_PAREN args RIGHT_PAREN
let call: Parser<AST> =
  ID.bind((callee) =>
    LEFT_PAREN.and(args.bind((args) =>
      RIGHT_PAREN.and(
        constant(new Call(callee, args))))));
```

## Atom

The next parser is `atom`.
To ensure that it produces an AST, we need to use `id` rule instead of `ID`.
We also bind the `expression` to extract its value.

```js
// atom <- call / ID / NUMBER
//       / LEFT_PAREN expression RIGHT_PAREN
let atom: Parser<AST> =
  call.or(id).or(NUMBER).or(
    LEFT_PAREN.and(expression).bind((e) =>
      RIGHT_PAREN.and(constant(e))));
```

The order of the choices is important.
If the rule started as `ID / call` instead, `call` would never match, since `call` itself begins with an `ID`.

## Unary operators

For unary parser, we bind both `NOT?` and `atom`.
If `NOT` operator is present we construct the `Not` AST node,
otherwise, we produce the underlying node.

```js
// unary <- NOT? atom
let unary: Parser<AST> =
  maybe(NOT).bind((not) =>
    atom.map((term) => not ? new Not(term) : term));
```

We have bound the value of the `atom` to a name `term`, which we will use as a catch-all phrase when binding expressions or statements.

## Infix operators

<!-- TODO "precedence language confusing: lower is higher, higher is lower? -->

Infix operators are all constructed similarly, with lower precedence rules building upon higher precedence rules.

```
product <- unary ((STAR / SLASH) unary)*
sum <- product ((PLUS / MINUS) product)*
comparison <- sum ((EQUAL / NOT_EQUAL) sum)*
```

You can probably remember that we made sure that operator rule parsers produce the class of the corresponding AST node.
For example, the `EQUAL` token produces the `Equal` class.
We will use that property.

We'll start with the `product` parser.
Naive mechanical translation gives us:

```js
// product <- unary ((STAR / SLASH) unary)*
let product =
  unary.and(zeroOrMore(STAR.or(SLASH).and(unary)));
```

Binding the first `unary` is easy.
However, constructing a nested AST from all of this is not.

We can map `(STAR / SLASH) unary` to an intermediate data structure `{operator, term}`, which is a pair constructed from `STAR / SLASH` and `unary` values.
This way, we get an array of operator-term pairs.
We bind the `unary` and call its value `first`.

For example, if we were parsing a string `"x * y / z"`, then `first` would be `new Id("x")`, while `operatorTerms` would be an array like this:

```js
[
  {operator: Multiply, term: new Id("y")},
  {operator: Divide,   term: new Id("z")},
]
```

How do we reduce those into an AST node like the following?

```js	
new Divide(
  new Multiply(new Id("x"), new Id("y")),
  new Id("z"))
```

Turns out that `array.reduce` is precisely the method that can accomplish this!
Here's the resulting code:

```js
// product <- unary ((STAR / SLASH) unary)*
let product =
  unary.bind((first) =>
    zeroOrMore(STAR.or(SLASH).bind((operator) =>
      unary.bind((term) =>
        constant({operator, term})))).map((operatorTerms) =>
          operatorTerms.reduce((left, {operator, term}) =>
            new operator(left, term), first)));
```

Quite a mouthful!
Fortunately, this is the most complicated rule that we will encounter.
Even better, we can extract this repeating pattern into another parser combinator and use it again.
We'll call that combinator `infix`:

```js
let infix = (operatorParser, termParser) =>
  termParser.bind((term) =>
    zeroOrMore(operatorParser.bind((operator) =>
      termParser.bind((term) =>
        constant({operator, term})))).map((operatorTerms) =>
          operatorTerms.reduce((left, {operator, term}) =>
            new operator(left, term), term)));
```

We changed our `product` rule into a function that takes two parameters: `operatorParser` and `termParser`.
We replaced `unary` with `termParser` and `STAR.or(SLASH)` with `operatorParser`.
And now we've got a reusable combinator, which we can use not only for `product` but also for `sum` and `comparison`.

```js
// product <- unary ((STAR / SLASH) unary)*
let product = infix(STAR.or(SLASH), unary);

// sum <- product ((PLUS / MINUS) product)*
let sum = infix(PLUS.or(MINUS), product);

// comparison <- sum ((EQUAL / NOT_EQUAL) sum)*
let comparison = infix(EQUAL.or(NOT_EQUAL), sum);
```

## Associativity

When we parse `"x * y / z"` we want it to be interpreted as `"(x * y) / z"` and produce the corresponding AST:

```js
new Divide(
  new Multiply(new Id("x"), new Id("y")),
  new Id("z"))
```

Thus, we say that these operators are left-associative.
At the moment we don't have any right-associative operators, but if we did, we would use the same grammar rules, but we would have to use `array.reduceBack` instead of `array.reduce` to construct the AST, with some adjustments.

## Closing the loop: expression

Now that we have defined `comparison`, we can finally define `expression` which had only a dummy implementation so far.
We do that by overwriting the `parse` method of `expression`:

```js
// expression <- comparison
expression.parse = comparison.parse;
```

## Statement

Next up is parsing statements.
Here's the grammar:

```
returnStatement <- RETURN expression SEMICOLON

expressionStatement <- expression SEMICOLON

ifStatement <-
  IF LEFT_PAREN expression RIGHT_PAREN
    statement
  ELSE
    statement

whileStatement <-
  WHILE LEFT_PAREN expression RIGHT_PAREN statement

varStatement <- VAR ID ASSIGN expression SEMICOLON

assignmentStatement <- ID ASSIGN EXPRESSION SEMICOLON

blockStatement <- LEFT_BRACE statement* RIGHT_BRACE

parameters <- (ID (COMMA ID)*)?

functionStatement <-
  FUNCTION ID LEFT_PAREN parameters RIGHT_PAREN
  blockStatement

statement <- returnStatement
           / ifStatement
           / whileStatement
           / varStatement
           / assignmentStatemnt
           / blockStatement
           / functionStatement
           / expressionStatement
```

The high-level structure is very similar, as in the case of expressions.
It consists of several rules, with `statement` defined recursively.
Again, we start with a dummy implementation:

```js
let statement: Parser<AST> =
  Parser.error(
    "Statement parser used before definition");
```

First statement kind is `returnStatment` that produces the `Return` AST node:

```js
// returnStatement <- RETURN expression SEMICOLON
let returnStatement: Parser<AST> =
  RETURN.and(expression).bind((term) =>
    SEMICOLON.and(constant(new Return(term))));
```

The `expressionStatement` is an `expression` delimited with a semicolon:

```js
// expressionStatement <- expression SEMICOLON
let expressionStatement: Parser<AST> =
  expression.bind((term) =>
    SEMICOLON.and(constant(term)));
```

\newpage

The `ifStatement` produces the `If` node:

```js
// ifStatement <-
//   IF LEFT_PAREN expression RIGHT_PAREN
//     statement
//   ELSE
//     statement
let ifStatement: Parser<AST> =
  IF.and(LEFT_PAREN).and(expression).bind(
    (conditional) =>
      RIGHT_PAREN.and(statement).bind((consequence) =>
        ELSE.and(statement).bind((alternative) =>
          constant(new If(conditional,
                          consequence,
                          alternative)))));
```

The `whileStatment` is syntactically similar to the `ifStatement`:

```js
// whileStatement <-
//   WHILE LEFT_PAREN expression RIGHT_PAREN statement
let whileStatement: Parser<AST> =
  WHILE.and(LEFT_PAREN).and(expression).bind(
    (conditional) =>
      RIGHT_PAREN.and(statement).bind((body) =>
        constant(new While(conditional, body))));
```

The `varStatment` and the `assigmentStatement` are similar as well:

```js
// varStatement <-
//   VAR ID ASSIGN expression SEMICOLON
let varStatement: Parser<AST> =
  VAR.and(ID).bind((name) =>
    ASSIGN.and(expression).bind((value) =>
      SEMICOLON.and(constant(new Var(name, value)))));
```

```js
// assignmentStatement <- ID ASSIGN EXPRESSION SEMICOLON
let assignmentStatement: Parser<AST> =
  ID.bind((name) =>
    ASSIGN.and(expression).bind((value) =>
      SEMICOLON.and(constant(new Assign(name, value)))));
```

Technically speaking, in JavaScript, the assignment is an expression, but for simplicity, we defined it as a statement.
That's also how it is used most of the time.

\newpage

The block statement is a list of statements delimited with braces.
It produces a `Block` node:


```js
// blockStatement <- LEFT_BRACE statement* RIGHT_BRACE
let blockStatement: Parser<AST> =
  LEFT_BRACE.and(zeroOrMore(statement)).bind(
    (statements) =>
      RIGHT_BRACE.and(constant(new Block(statements))));
```

Function parameters rule is very similar to the `args` rule that we defined previously (in terms of parser structure), but the parser produces an `Array<string>` instead of `Array<AST>`:

```js
// parameters <- (ID (COMMA ID)*)?
let parameters: Parser<Array<string>> =
  ID.bind((param) =>
    zeroOrMore(COMMA.and(ID)).bind((params) =>
      constant([param, ...params]))).or(constant([]))
```

The function definition (which we also refer to as a statement) builds upon `parameters` and `blockStatement` to produce a `Function` node:

```js
// functionStatement <-
//   FUNCTION ID LEFT_PAREN parameters RIGHT_PAREN
//   blockStatement
let functionStatement: Parser<AST> =
  FUNCTION.and(ID).bind((name) =>
    LEFT_PAREN.and(parameters).bind((parameters) =>
      RIGHT_PAREN.and(blockStatement).bind((block) =>
        constant(
          new Function(name, parameters, block)))));
```

We define `statement` as one of the above statements, and we tie the recursive knot by modifying the original `statement.parser`.

```js		
// statement <- returnStatement
//            / ifStatement
//            / whileStatement
//            / varStatement
//            / assignmentStatement
//            / blockStatement
//            / functionStatement
//            / expressionStatement
```

\newpage

```js
let statementParser: Parser<AST> =
  returnStatement
    .or(functionStatement)
    .or(ifStatement)
    .or(whileStatement)
    .or(varStatement)
    .or(assignmentStatement)
    .or(blockStatement)
    .or(expressionStatement);

statement.parse = statementParser.parse;
```

And since our language should accept more than one statement, we need one final touch to complete our parser:

```js
let parser: Parser<AST> =
  ignored.and(zeroOrMore(statement)).map((statements) =>
    new Block(statements));
```

It starts with allowing the "ignored" whitespace and comments (which need to be explicitly ignored before the first logical token) and follows by zero or more statements that we convert to a `Block` node.

## Testing

It is essential to test the parser at each step of the way.
The examples from the chapter *Abstract Syntax Tree* provide a good source of unit tests.
And here's an example of a possible integration test:

```js
let source = `
  function factorial(n) {
    var result = 1;
    while (n != 1) {
      result = result * n;
      n = n - 1;
    }
    return result;
  }
`;
```

\newpage

```js
let expected = new Block([
  new Function("factorial", ["n"], new Block([
    new Var("result", new Number(1)),
    new While(new NotEqual(new Id("n"),
                           new Number(1)), new Block([
      new Assign("result", new Multiply(new Id("result"),
                                        new Id("n"))),
      new Assign("n", new Subtract(new Id("n"),
                                   new Number(1))),
    ])),
    new Return(new Id("result")),
  ])),
]);

let result = parser.parseStringToCompletion(source);

console.assert(result.equals(expected));
```

* * *

<center><p>The parser is now complete, and so is the first pass of our compiler.<p></center>

<!--\begin{center}The parser is now complete, and so is the first pass of our compiler. \end{center}-->

<!--\newpage
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}-->

```{=html}
<center><a href="./07-arm-assembly-programming#fold">Next: Chapter 7. ARM Assembly Programming</a></center>
```
