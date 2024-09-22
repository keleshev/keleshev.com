---
title: "4. Abstract Syntax Tree • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 4</small></small> <br/>Abstract Syntax Tree<br/><br/></h1>
```


\chapter{Abstract Syntax Tree}
\includegraphics{chapter-illustrations/4.png}
\newpage

Abstract syntax tree, or AST, is the central concept in compilers.

AST is a data-structure.
It's a *tree* that models the *syntax* of a programming language.
But it *abstracts* away from the mundane details of syntax, such as the exact placement of parenthesis or semicolons.

<!-- TODO CJlambda suggested a high-level definition of syntax -->

This tree consists of *nodes*, where each node is a data object that represents a syntactic construct in the language.
A `Return` node could represent a `return`{.js} statement,
an `Add` node can represent a `+` operator,
an identifier referring to a variable could use an `Id` node, and so on.

For example, the following line of code:

```js
return n * factorial(n - 1);
```

Can have an AST like this:

```js
new Return(
  new Multiply(
    new Id("n"),
    new Call("factorial", [
      new Subtract(new Id("n"), new Number(1)),
    ])))
```

In the next figure you can see a graphical representation of the same tree.

![AST corresponding to `\texttt{\textbf{return }}`{=tex}`<code><b>return </b></code>`{=html}`n * factorial(n - 1)`](figures/ast-example.svg){width=75%}

Why use an AST?
When working with a language construct, an AST makes it convenient to operate on it: to query, construct, and modify.

<!--
Say, you want to add a parameter `p` to a call, given some existing call `myCall`?
We can construct this new call, by quering `myCall` for its callee and arguments fields:

    new Call(myCall.callee, [new Id("p"), ...myCall.args])
-->

We design an AST so that it is convenient for us, depending on what we do with it: what kinds of transformations we want to make, which things to query or change.

For example, an AST can include source location information for error reporting.
Or it can include documentation comments if our compiler needs to deal with those.
Or it can include all comments and some notion of whitespace, if we want to have style-preserving transformations, like automatic refactoring.

> **Well, actually…**
>
> There are also *concrete syntax trees*, also called *parse trees*.
> They reflect the structure and hierarchy down to *each* input symbol.
> They usually have too many details that we don't care about when writing a compiler.
> But they are a good match for style-preserving transformations.

We will represent each kind of node in our AST as a separate class: `Return`, `Multiply`, `Id`, etc.
However, at the type level, we want to be able to refer to "any AST node".
For that TypeScript gives us several tools:

 * interfaces,
 * abstract classes,
 * union types.

Either of these works.
We will use an interface:

```js
interface AST {
  equals(other: AST): boolean;
}
```

Each type of AST node will be a class that implements the `AST` interface.
It starts simple, with `equals` as the only method.
We will add methods to this interface (and the classes) as needed.

The `equals` method is mostly useful for unit-testing.
The implementation is quite mundane, so for the most part, we will omit it and replace its body with an ellipsis.

## Number node

Our first node is `Number`.

```js
class Number implements AST {
  constructor(public value: number) {}

  equals(other: AST) {…}
}
```

Here we used the TypeScript shortcut for quickly defining instance variables using `public`{.js} for the constructor parameter.
Remember that it is equivalent to the following:

```js
class Number implements AST {
  public value: number;

  constructor(value: number) {
    this.value = value;
  }

  equals(other: AST) {…}
}
```

It saves us quite some typing, which will be useful because we need to define many types of AST nodes.

We called our AST node `Number` because the data type in JavaScript and TypeScript is called `number`.
However, our compiler will handle only unsigned integers.

Table: Examples of the `Number` node

+--------+-----------------------+
| Source | AST                   |
+========+======================:+
| `0`    | `new Number(0)`{.js}  |
+--------+-----------------------+
| `42`   | `new Number(42)`{.js} |
+--------+-----------------------+

\newpage

## Identifier node

Identifiers, or *id*s for short, refer to variables in the code.

```js
class Id implements AST {
  constructor(public value: string) {}

  equals(other: AST) {…}
}
```

+---------+------------------------+
| Source  |                    AST |
+=========+=======================:+
| `x`     | `new Id("x")`{.js}     |
+---------+------------------------+
| `hello` | `new Id("hello")`{.js} |
+---------+------------------------+

Table: Examples of the `Id` node

## Operator nodes

The next AST node is `Not`, which stands for the logical negation operator (`!`).

```js
class Not implements AST {
  constructor(public term: AST) {}

  equals(other: AST) {…}
}
```

+--------+--------------------------------+
| Source |                            AST |
+========+===============================:+
| `!x`   | `new Not(new Id("x"))`{.js}    |
+--------+--------------------------------+
| `!42`  | `new Not(new Number(42))`{.js} |
+--------+--------------------------------+

Table: Examples of the `Not` node

Negation is the only *prefix operator* (or *unary operator*) that we define.
However, we define several *infix operators* (or *binary operators*).

Equality operator (`==`) and its opposite (`!=`).

\newpage

```js
class Equal implements AST {
  constructor(public left: AST, public right: AST) {}

  equals(other: AST) {…}
}
```

```js
class NotEqual implements AST {
  constructor(public left: AST, public right: AST) {}

  equals(other: AST) {…}
}
```

Table: Examples of `Equal` and `NotEqual` nodes

+-----------+-------------------------------------------------------------------+
| Source    |                          AST                                      |
+===========+==================================================================:+
| `x == y`  | `new Equal(new Id("x"), new Id("y"))`{.js}                        |
+-----------+-------------------------------------------------------------------+
| `10 != 25`| `new NotEqual(new Number(10), new Number(25))`{.js}               |
+-----------+-------------------------------------------------------------------+
                                                                          

Addition (`+`), subtraction (`-`), multiplication (``*``), and division (`/`):

```js
class Add implements AST {
  constructor(public left: AST, public right: AST) {}

  equals(other: AST) {…}
}
```

```js
class Subtract implements AST {
  constructor(public left: AST, public right: AST) {}

  equals(other: AST) {…}
}
```

```js
class Multiply implements AST {
  constructor(public left: AST, public right: AST) {}

  equals(other: AST) {…}
}
```


```js
class Divide implements AST {
  constructor(public left: AST, public right: AST) {}

  equals(other: AST) {…}
}
```

\newpage

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{}#1}

Table: Examples of `Add` and `Multiply` nodes

+----------------------------------+-------------------------------------------+
|  Source                          |                                      AST  |
+==================================+==========================================:+
|                                  | ```js                                     |
| `x + y`                          |           new Add(new Id("x"),            |
|                                  |                   new Id("y"))            |
|                                  | ```                                       |
+----------------------------------+-------------------------------------------+
|                                  |                                           |
+----------------------------------+-------------------------------------------+
|                                  | ```js                                     |
| `10 * 25`                        |   new Multiply(new Number(10),            |
|                                  |                new Number(25))            |
|                                  | ```                                       |
+----------------------------------+-------------------------------------------+
                                                                    
  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{} ~#1}


Note that since the parameters are ASTs themselves, that means they can be arbitrarily nested.

For example, `42 + !(20 != 10)` will be:

```js
new Add(new Number(42),
        new Not(new NotEqual(new Number(20),
                             new Number(10))))
```

Not all combinations of AST nodes make sense.
Nonetheless, the one above happens to be valid in JavaScript.


## Call node

`Call` refers to a function name (or *callee*), and an array of arguments.
For example, `f(x)` becomes: `new Call("f", [new Id("x")])`{.js}.

```js
class Call implements AST {
  constructor(public callee: string,
              public args: Array<AST>) {}

  equals(other: AST) {
    return other instanceof Call &&
      this.callee === other.callee &&
      this.args.length === other.args.length &&
      this.args.every((arg, i) =>
        arg.equals(other.args[i]));
  }
}
```

The language of our baseline compiler is restricted such that only named functions can be called.

We can't name the arguments array `arguments`, since this clashes with JavaScript built-in `arguments` object.
So, with some reluctance, let's call it `args`.

The `Call` node is interesting because it has both a primitive string and an array of AST as its members.
JavaScript doesn't have an agreed-upon protocol for equality; that's why `Call` makes an excellent example of how to implement the `equals` method in JavaScript:

* It uses `instanceof`{.js} operator to check that the other AST is also a `Call`.
* It compares the `callee` strings using the `===` operator.
* It uses the `.equals` method for comparing AST nodes of each argument.
* It compares array by length and checks `every` element.

Languages other than JavaScript often have more elegant ways of dealing with structural equality.

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{}#1}

Table: Examples of the `Call` node

+------------------------------+-----------------------------------------------+
| Source                       | AST                                           |
+==============================+==============================================:+
|                              | ```js                                         |
| `f(x, y)`                    |   new Call("f", [                             |
|                              |     new Id("x"),                              |
|                              |     new Id("y"),                              |
|                              |   ])                                          |
|                              | ```                                           |
+------------------------------+-----------------------------------------------+
|                              |                                               |
+------------------------------+-----------------------------------------------+
|                              | ```js                                         |
| `factorial(n - 1)`           |   new Call("factorial", [                     |
|                              |     new Subtract(new Id("n"),                 |
|                              |                  new Number(1)),              |
|                              |   ])                                          |
|                              | ```                                           |
+------------------------------+-----------------------------------------------+
                                                                         
  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{} ~#1}


## Return node

```js
class Return implements AST {
  constructor(public term: AST) {}

  equals(other: AST) {…}
}
```

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{}#1}

Table: Examples of the `Return` node

+----------------------------------+-------------------------------------------+
| Source                           | AST                                       |
+==================================+==========================================:+
|                                  | ```js                                     |
| `return 0;`{.js}                 | new Return(new Number(0))                 |
|                                  | ```                                       |
+----------------------------------+-------------------------------------------+
|                                  |                                           |
+----------------------------------+-------------------------------------------+
|                                  | ```js                                     |
| `return n - 1;`{.js}             | new Return(                               |
|                                  |   new Subtract(new Id("n"),               |
|                                  |                new Number(1)))            |
|                                  | ```                                       |
+----------------------------------+-------------------------------------------+

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{} ~#1}


## Block node

`Block` refers to a block of code delimited with curly braces.

```js
class Block implements AST {
  constructor(public statements: Array<AST>) {}

  equals(other: AST) {…}
}
```

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{}#1}

Table: Examples of the `Block` node

+----------------------------------+-------------------------------------------------+
| Source                           | AST                                             |
+==================================+================================================:+
| ```js                            | ```js                                           |
| {}                               | new Block([])                                   |
| ```                              | ```                                             |
+----------------------------------+-------------------------------------------------+
|                                  |                                                 |
+----------------------------------+-------------------------------------------------+
| ```js                            | ```js                                           |
| {                                | new Block([                                     |
|   f(x);                          |   new Call("f", [new Id("x")]),                 |
|   return y;                      |   new Return(new Id("y")),                      |
| }                                | ])                                              |
| ```                              | ```                                             |
+----------------------------------+-------------------------------------------------+
                                                                                
  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{} ~#1}

## If node

The `If` node has three branches:

 * `conditional` refers to the expression that is evaluated to either true or false,
 * `consequence` is the branch taken in the true case, and
 * `alternative` is the branch taken in the false case.

<!-- -->

\newpage

```js
class If implements AST {
  constructor(public conditional: AST,
              public consequence: AST,
              public alternative: AST) {}

  equals(other: AST) {…}
}
```

This way, the following:

```js
if (x == 42) {
  return x;
} else {
  return y;
}
```

Becomes:

```js
new If(
  new Equal(new Id("x", new Number(42))),
  new Block([new Return(new Id("x"))]),
  new Block([new Return(new Id("y"))]),
)
```  

Curly braces are optional for if statements, thus, the following:

```js
if (x == 42)
  return x;
else
  return y;
```

Becomes:

```js
new If(
  new Equal(new Id("x", new Number(42))),
  new Return(new Id("x")),
  new Return(new Id("y")),
)
```

How do we represent an `if`{.js} without the `else`{.js} branch?
We could have a separate node for it, or we can do a simple trick: representing `if (x) y`{.js} the same way as `if (x) y else {}`{.js}.
In other words, by placing an empty `Block` as the `alternative`.


## Function definition node

A function definition consists of a function name, an array of parameters, and the function's body.

```js
class Function implements AST {
  constructor(public name: string,
              public parameters: Array<string>,
              public body: AST) {}

  equals(other: AST) {…}
}
```

<!-- TODO talk about global and module scope, export/import keyword gotcha -->

Consider the following function definition.

```js
function f(x, y) {
  return y;
}
```

When converted to an AST it becomes as follows.

```js
new Function("f", ["x", "y"], new Block([
  new Return(new Id("y")),
]))
```

Notice that in a function definition, the parameters are strings, while in a function call, they are ASTs.
This fact reflects that function calls can have nested expressions, while function definitions simply list the inbound variable names.

## Variable declaration node

`Var` nodes are for variable declarations.
So `var x = 42;`{.js} becomes `new Var("x", new Number(42))`{.js}.

```js
class Var implements AST {
  constructor(public name: string, public value: AST) {}

  equals(other: AST) {…}
}
```


<!-- Removed for page alignment

Table: Examples of the `Var` node

+-----------------------+------------------------------------------------------+
| Source                | AST                                                  |
+=======================+======================================================+
|                       | ```js                                                |
| `var x = 42;`{.js}    | new Var("x", new Number(42))                         |
|                       | ```                                                  |
+-----------------------+------------------------------------------------------+
|                       | ```js                                                |
| `var y = a + b;`{.js} | new Var("y", new Add(new Id("a"),                    |
|                       |                      new Id("b")))                   |
|                       | ```                                                  |
+-----------------------+------------------------------------------------------+
-->

## Assignment node

An assignment is represented with the node `Assign`.

```js
class Assign implements AST {
  constructor(public name: string,
              public value: AST) {}

  equals(other: AST) {…}
}
```

Assignment differs from variable declaration in the following way: assignment changes the value of an existing variable, and does not define a new one.
At least, that's the distinction that we will assume.
JavaScript allows assignment of a variable that is not defined yet; in such case, it will create a global variable.
TypeScript, on the other hand, dissallows this error-prone behavior.

Table: Examples of the `Assign` node

+--------------------------+--------------------------------------------------+
| Source                   | AST                                              |
+==========================+=================================================:+
|                          | ```js                                            |
| `x = 42;`{.js}           | new Assign("x", new Number(42))                  |
|                          | ```                                              |
+--------------------------+--------------------------------------------------+
|                          |                                                  |
+--------------------------+--------------------------------------------------+
|                          | ```js                                            |
| `y = a + b;`{.js}        | new Assign("y",                                  |
|                          |            new Add(new Id("a"),                  |
|                          |                    new Id("b"))))                |
|                          | ```                                              |
+--------------------------+--------------------------------------------------+
                                                                     

## While loop node

The last node of our AST and the last construct in our baseline language is the while loop.

```js
class While implements AST {
  constructor(public conditional: AST,
              public body: AST) {}

  equals(other: AST) {…}
}
```

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{}#1}

Table: Examples of the `While` node

+-------------------------+---------------------------------------------+
| Source                  | AST                                         |
+=========================+============================================:+
| ```js                   | ```js                                       |
| while (x)               | new While(                                  |
|   f();                  |   new Id("x"),                              |
|                         |   new Call("f", []))                        |
| ```                     | ```                                         |
+-------------------------+---------------------------------------------+
|                         |                                             |
+-------------------------+---------------------------------------------+
| ```js                   | ```js                                       |
| while (x) {             | new While(new Id("x"), new Block([          |
|   f();                  |   new Call("f", []),                        |
| }                       | ]))                                         |
| ```                     | ```                                         |
+-------------------------+---------------------------------------------+
                      
  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{} ~#1}

## Summary

Let's look at a larger snippet converted to an AST.
Remember our factorial function:


```js
function factorial(n) {
  var result = 1;
  while (n != 1) {
    result = result * n;
    n = n - 1;
  }
  return result;
}
```

And here is the corresponding AST:

```js
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
]))
```


We finish this chapter with a table that summarizes all the AST constructors that we've covered, their signatures, and examples of what source code these AST nodes can represent.

<!--
Why did we choose to represent each node with its own class?
Why do we have to use classes, and not some data format such as JSON?
That's because we want to use the most powerful control-flow method available in the language to deal with ASTs.
-->

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{}#1}

Table: Summary of AST constructor signatures with examples

+-------------------------------------------------------+----------------------------------+
| AST Constructor Signature                             | Example                          |
+=======================================================+=================================:+
| ```js                                                 | ```js                            |
| Number(value: number)                                 | 42                               |
| Id(value: string)                                     | x                                |
| Not(term: AST)                                        | !term                            |
| Equal(left: AST, right: AST)                          | left == right                    |
| NotEqual(left: AST, right: AST)                       | left != right                    |
| Add(left: AST, right: AST)                            | left + right                     |
| Subtract(left: AST, right: AST)                       | left - right                     |
| Multiply(left: AST, right: AST)                       | left * right                     |
| Divide(left: AST, right: AST)                         | left / right                     |
| ```                                                   | ```                              |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
| ```js                                                 | ```js                            |
| Call(callee: string,                                  | callee(a1, a2, a3)               |
|      args: Array<AST>)                                | ```                              |
| ```                                                   |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
| ```js                                                 | ```js                            |
| Return(term: AST)                                     | return term;                     |
| ```                                                   | ```                              |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
| ```js                                                 | ```js                            |
| Block(statements: Array<AST>)                         | { s1; s2; s3; }                  |
| ```                                                   | ```                              |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
| ```js                                                 | ```js                            |
| If(conditional: AST,                                  | if (conditional)                 |
|    consequence: AST,                                  |   consequence                    |
|    alternative: AST)                                  | else                             |
| ```                                                   |   alternative                    |
|                                                       | ```                              |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
| ```js                                                 |                                  |
| Function(                                             | ```js                            |        
|   name: string,                                       | function name(p1) {              |        
|   parameters: Array<string>,                          |   body;                          |        
|   body: AST,                                          | }                                |        
| )                                                     | ```                              |        
| ```                                                   |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
| ```js                                                 | ```js                            |
| Var(name: string,                                     | var name = value;                |
|     value: AST)                                       | ```                              |
| ```                                                   |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
| ```js                                                 | ```js                            |
| Assignment(name: string,                              | name = value;                    |
|            value: AST)                                | ```                              |
| ```                                                   |                                  |
+-------------------------------------------------------+----------------------------------+
|                                                       |                                  |
+-------------------------------------------------------+----------------------------------+
| ```js                                                 | ```js                            |
| While(conditional: AST,                               | while (conditional)              |
|       body: AST)                                      |   body;                          |
| ```                                                   | ```                              |
+-------------------------------------------------------+----------------------------------+

  \renewcommand{\FancyVerbFormatLine}[1]{%
  \makebox[0.0cm][l]{} ~#1}

In the next two chapters, you will learn about converting a program from source to an AST, or in other words, about *parsing*.


```{=html}
<center><a href="./05-parser-combinators#fold">Next: Chapter 5. Parser Combinators</a></center>
```
