---
title: "13. Static Type Checking and Inference • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 13</small></small><br/>Static Type Checking<small style="line-height:0"><small><small><br/>and<br/></small></small></small>Inference<br/><br/></h1>
```

\newpage
\setcounter{page}{162}
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center} 

\chapter{Static Type Checking and Inference}
\includegraphics{chapter-illustrations/13.png}
\newpage


In this chapter, we will implement a type checker for our language with *local type inference*.
Local type inference means that local variables do not need a type annotation,
so you can write the following:

```js
let a = [1, 2, 3];
```

The type of `a` will be inferred as `Array<number>`.

Our type checker will cover such types as `number`{.js}, `boolean`{.js}, `void`{.js}, and `Array<T>` where `T` could be any other type, for example `Array<Array<boolean>>`.
We will also deal with function types, such as `(x: boolean, y: number) => number`, when type checking function calls.

First, we need to refer to different types to manipulate them.
We will represent them similarly to AST nodes, with an interface called `Type` and one class that implements it per type.

```js
interface Type {
  equals(other: Type): boolean;
  toString(): string;
}
```

We will need equality and a `toString` method to be able to display type errors.

Table: Summary of Type constructor signatures with examples

+--------------------------------------------------------------+---------------------------------------+
| Type Constructor Signature                                   | Example                               |
+==============================================================+=======================================+
| ```js                                                        | ```js                                 |
| BooleanType()                                                | boolean                               |
| ```                                                          | ```                                   |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
| ```js                                                        | ```js                                 |
| NumberType()                                                 | number                                |
| ```                                                          | ```                                   |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
| ```js                                                        | ```js                                 |
| VoidType()                                                   | void                                  |
| ```                                                          | ```                                   |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
| ```js                                                        | ```js                                 |
| ArrayType(element: Type)                                     | Array<number>                         |
| ```                                                          | ```                                   |
+--------------------------------------------------------------+---------------------------------------+
|                                                              |                                       |
+--------------------------------------------------------------+---------------------------------------+
|     FunctionType(                                            |     (x: boolean,                      |
|       parameters: Map<string, Type>,                         |      y: number)                       |
|       returnType: Type,                                      |       => number                       |
|     )                                                        |                                       |
+--------------------------------------------------------------+---------------------------------------+

\newpage
                                                    
Implementing `toString` and `equals` for these data classes is straightforward.
However, `FunctionType` requires some comments:

  * First, `Map` in JavaScript preserves the order of elements, which is important to be able to match parameter positions at a call site.
  * When comparing two instances of `FunctionType` it makes sence to ignore parameter names, since `(x: boolean, y: number) => number` is the same type as `(p1: boolean, p2: number) => number`.

Our language will change to allow functions to be type-annotated.
We will first change our `Function` AST node to store its signature as `FunctionType`, instead of just parameter names:

```js
class Function implements AST {
  constructor(public name: string,
              public signature: FunctionType,
              public body: AST) {}

  visit<T>(v: Visitor<T>) {…}

  equals(other: AST): boolean {…}
}
```

We will also need to change our grammar and parser.
After introducing the necessary tokens, we can define the following grammar for types.

```js
arrayType <- ARRAY LESS_THAN type GREATER_THAN
type <- VOID | BOOLEAN | NUMBER | arrayType
```

The `type` rule is recursive, just like `expression` and `statement`.

Next, we need to change the grammar and parser for functions, to include optional type annotations:

```
optionalTypeAnnotation <- (COLON type)?
parameter <- ID optionalTypeAnnotation
parameters <- (parameter (COMMA parameter)*)?
functionStatement <-
  FUNCTION ID LEFT_PAREN
    parameters
  RIGHT_PAREN optionalTypeAnnotation
    blockStatement
```

We allow optional type annotations for function parameters and function return type.
Why optional?
Some languages do infer parameter and return types, but we do it so we can use the same parser unmodified later with dynamic types.
If a type annotation is missing, we default it to `number`, which also gives us some backwards compatibility with our test suite.

Now, the parser will accept functions with type annotations, like the following:

```js
function pair(x: number, y: number): Array<number> {
  return [x, y];
}
```

For such function, the parser will produce a `Function` node with `FunctionType` signature like this:

```js
new Function(
  "pair",
  new FunctionType(
    new Map([["x", new NumberType()],
             ["y", new NumberType()]]),
    new ArrayType(new NumberType()),
  ),
  new Block([
    new Return(new ArrayLiteral([new Id("x"),
                                 new Id("y")])),
  ]),
)
```

Next, for type checking, we will use a function that asserts that two types are the same and otherwise raises an exception to signal an error.
We call it `assertType`:

```js
function assertType(expected: Type, got: Type): void {
  if (!expected.equals(got)) {
    throw TypeError(
      `Expected ${expected}, but got ${got}`);
  }
}
```

It uses both the `equals` method and the `toString` method, which is invoked implicitly for template string variables.
Here, we are slightly abusing the built-in `TypeError` exception, which has a different purpose (run-time type errors); it is better to define a custom exception type.

Our `TypeChecker` pass will walk the AST and will either abort with a `TypeError`, or will return the inferred `Type` of an expression.
Thus, `TypeChecker` implements `Visitor<Type>`.

```js
class TypeChecker implements Visitor<Type> {
  constructor(
    public locals: Map<string, Type>,
    public functions: Map<string, FunctionType>,
    public currentFunctionReturnType: Type | null,
  ) {}

  …
}
```

It maintains two environments:

 * `locals`—an environment that stores types of local variables in a function, and
 * `functions`—an environment that stores signatures of each function.

We need two separate environments for these since functions are not first-class in our language: they cannot be assigned to a variable and passed around.
So, when we encounter a `Call`, we will search for a function in the `functions` map, and when we encounter an `Id`, we will search for a non-function type in the `locals` map.

We also maintain an instance variable `currentFunctionReturnType` which will help us type-check `Return` statements.

Now, we get to the actual type checking and inference.

## Scalars

The type of literal scalars is the easiest to infer.
We know that the type of a number literal is `number`, the type of a boolean node is `boolean`, and so forth.

```js
  visitNumber(node: Number) {
    return new NumberType();
  }
  
  visitBoolean(node: Boolean) {
    return new BooleanType();
  }
```

In TypeScript the `void`{.js} type is inferred for expressions or statements that return `undefined`{.js}.

```js
  visitUndefined(node: Undefined) {
    return new VoidType();
  }
```

## Operators

Now, let's look at the most straightforward operator—negation.
That's not exactly how it works in TypeScript, but let's assume that the negation operator expects strictly boolean parameter.
To enforce that, we first infer the inner term's type by calling the `visit` method on it.
Then we assert that it is boolean:

```js
  visitNot(node: Not) {
    assertType(new BooleanType(), node.term.visit(this));
    return new BooleanType();
  }
```

We return the `boolean` type since this will always be the result of negation.

To type-check numeric operators like `Add`, we infer the type of `left` and `right` parameters and assert that they are both numbers.
Then we return `number` as the resulting type.

```js
  visitAdd(node: Add) {
    assertType(new NumberType(), node.left.visit(this));
    assertType(new NumberType(), node.right.visit(this));
    return new NumberType();
  }
```

Now we get to something more interesting.
Operations such as equality are generic: they can work with any type as long as the type on the left-hand side is the same as the one on the right-hand side.
We infer the types on both sides by visiting them, and then assert that the two are the same.

\newpage

```js
  visitEqual(node: Equal) {
    let leftType = node.left.visit(this);
    let rightType = node.right.visit(this);
    assertType(leftType, rightType);
    return new BooleanType();
  }
```

## Variables

For a new variable defined with `var`{.js}, we infer its type by visiting its value, and then we add that type to the `locals` environment.

```js
  visitVar(node: Var) {
    let type = node.value.visit(this);
    this.locals.set(node.name, type);
    return new VoidType();
  }
```

When we encounter a variable, we look it up in the `locals` environment and return its type.
If the variable is not defined—we raise a `TypeError`.

<!--print layout omitttion: , which makes a similar check at the code generation level obsolete. -->

```js
  visitId(node: Id) {
    let type = this.locals.get(node.value);
    if (!type) {
      throw TypeError(`Undefined variable ${node.value}`);
    }
    return type;
  }
```

When assigning a new value to a variable, we check that the variable was previously defined, and that the assignment does not change the type of the variable.

<!--
When assigning a new value to a variable, we check two things:

* First, that the variable is previously defined.
* Second, that the assignment does not change the type of the variable.
-->

<!-- -->

```js
  visitAssign(node: Assign) {
    let variableType = this.locals.get(node.name);
    if (!variableType) {
      throw TypeError(`Undefined variable ${node.name}`);
    }
    let valueType = node.value.visit(this);
    assertType(variableType, valueType);
    return new VoidType();
  }
```



## Arrays

Inferring the type of array literals is a bit trickier than the other literals that we've covered.
We know that any array literal is of type `Array<T>`, but we need to figure out what `T` is.
First of all, we can't infer the type of an empty array—there's simply not enough information at this point.
There are bi-directional type inference algorithms that handle this, but often this is solved by requiring a type annotation.

If the array is non-empty, we infer the type of each element and then assert pair-wise that they are the same type.

```js
  visitArrayLiteral(node: ArrayLiteral): Type {
    if (node.args.length == 0) {
      throw TypeError("Can't infer type of empty array");
    }
    let argsTypes =
      node.args.map((arg) => arg.visit(this));
    let elementType = argsTypes.reduce((prev, next) => {
      assertType(prev, next);
      return prev;
    });
    return new ArrayType(elementType);
  }
```

<!--layout // Assert all arguments have the same type, pair-wise-->

For something like our array length primitive, we need to assert that the parameter type is an array, but we don't care about the element type.
So, instead of using `assertType` we manually check that the type is an instance of `ArrayType`, and raise a `TypeError` otherwise.
The inferred type of such expression is `number`.

```js
  visitLength(node: Length) {
    let type = node.array.visit(this);
    if (type instanceof ArrayType) {
      return new NumberType();
    } else {
      throw TypeError(`Expected an array, got: ${type}`);
    }
  }
```

\newpage

When handling array lookup, we assert that the `index` is a number, and that the `array` is of type array:

```js
  visitArrayLookup(node: ArrayLookup): Type {
    assertType(new NumberType(), node.index.visit(this));
    let type = node.array.visit(this);
    if (type instanceof ArrayType) {
      return type.element;
    } else {
      throw TypeError(`Expected an array, got: ${type}`);
    }
  }
```

## Functions

When encountering a function, we add its signature to the `functions` environment.
We do not need to infer it, because it is parsed from the source.
Before type-checking the body of the function, we create a new visitor with a modified environment.
Since we use mutable maps, we need to pass a new `Map` to each function, to avoid modifying the wrong function's environment.
We also set the `currentFunctionReturnType` to the one in the signature.

```js
  visitFunction(node: Function) {
    this.functions.set(node.name, node.signature);
    let visitor = new TypeChecker(
      new Map(node.signature.parameters),
      this.functions,
      node.signature.returnType,
    );
    node.body.visit(visitor);
    return new VoidType();
  }
```


When visiting a `Call`, we fetch that function's signature from the `functions` environment.
Then we infer the type of the function being called and compare it to the type from the environment.
When inferring the type of the function we visit each argument, and since `FunctionType` requires a name for each parameter, we assign them dummy names, such as `x0`, `x1`, `x2`, etc.
When it comes to the function's return type, we use the one from the type annotation.

\newpage

```js
  visitCall(node: Call) {
    let expected = this.functions.get(node.callee);
    if (!expected) {
      throw TypeError(`Function ${node.callee} undefined`);
    }
    let argsTypes = new Map();
    node.args.forEach((arg, i) =>
      argsTypes.set(`x${i}`, arg.visit(this))
    );
    let got =
      new FunctionType(argsTypes, expected.returnType);
    assertType(expected, got);
    return expected.returnType;
  }
```

When checking a return statement, we infer the type of the returned value and compare it with the one from the function annotation, which we saved conveniently in `currentFunctionReturnType` instance variable.

```js
  visitReturn(node: Return) {
    let type = node.term.visit(this);
    if (this.currentFunctionReturnType) {
      assertType(this.currentFunctionReturnType, type);
      return new VoidType();
    } else {
      throw TypeError(
        "Return statement outside of any function");
    }
  }
```

## If and While

When checking `If` and `While` we visit each inner node to make sure that their type is checked, but we don't enforce any type.
The `conditional` could be checked to be boolean, but in TypeScript (as in many languages) it is not required to be such.
We could also enforce that the statements inside the branches return `void`{.js}, but this is not usually required either.

\newpage

```js
  visitIf(node: If) {
    node.conditional.visit(this);
    node.consequence.visit(this);
    node.alternative.visit(this);
    return new VoidType();
  }
  
  visitWhile(node: While) {
    node.conditional.visit(this);
    node.body.visit(this);
    return new VoidType();
  }
```

However, if we had a ternary conditional operation, we would need to ensure that the two branches return the same type.

## Soundness

Our type checker is complete.
But is it *sound*?
A type system is sound if the types at compile time are always consistent with run time.
Can you find a soundness issue in our type checker?

Although we check that each `return`{.js} statement is consistent with the annotated return type, we don't check that each control-flow path has a return statement.
Here's an example that demonstraits this issue:

```js
function wrongReturnType(x: boolean): Array<number> {
  if (x) {
    return [42];
  }
}

function main() {
  var a = wrontReturnType(false);
  a[0]; // Segmentation fault
}
```

Checking that each control flow path leads to a return statement requires a bit of control-flow analysis which is outside of the scope of this book.

## Error messages

We can improve our error messages by specializing them to each situation instead of relying on a generic message produced by `assertType`.


```{=html}
<center><a href="./14-dynamic-typing#fold">Next: Chapter 14. Dynamic Typing</a></center>
```
