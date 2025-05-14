---
title: "12. Visitor Pattern • Compiling to Assembly from Scratch"
---

```{=html}
<header>
<h1><small><small>Chapter 12</small></small><br/>Visitor Pattern</h1>
<a href='./#table-of-contents'>Compiling to Assembly from Scratch</a>
<br/>by <a href='/'>Vladimir Keleshev</a>
</header>
```

\chapter{Visitor Pattern}
\includegraphics{chapter-illustrations/12.png}
\newpage

We are about to add more passes to our compiler: type checking, and code generation for dynamic typing.
What we could do is extend the AST interface with new methods, one for each pass.
It can look something like this:

```js
interface AST {
  emit(env: Environment): void;
  emitDynamic(env: Environment): void;
  typeCheck(env: TypeEnvironment): Type;
  equal(other: AST): boolean;
}
```

And this is perfectly fine.
However, this way, code for each pass is intertwined with code for every other pass.
In other words, code is grouped by an AST node and not by a pass.

Using the *visitor pattern* we can group the code for each pass together under a separate class.
The visitor pattern allows us to decouple our passes from AST by using indirection.
Instead of having a method *per pass, per AST node* we add a single method *per AST node* called `visit` that delegates the action to a class that implements the *visitor interface*.
The *visitor interface* has one method per AST node: `visitAssert`, `visitLength`, `visitNumber`, etc.

```js
interface AST {
  visit<T>(v: Visitor<T>): T;
  equal(other: AST): boolean;
}

interface Visitor<T> {
  visitAssert(node: Assert): T;
  visitLength(node: Length): T;
  visitNumber(node: Number): T;
  visitBoolean(node: Boolean): T;
  visitNot(node: Not): T;
  visitEqual(node: Equal): T;
  …
}
```

Each AST node implements the new `AST` interface by calling the corresponding visitor method.
For example, `Assert` calls `visitAssert`, `Length` calls `visitLength`, etc.

\newpage

```js
class Assert implements AST {
  constructor(public condition: AST) {}

  visit<T>(v: Visitor<T>) {
    return v.visitAssert(this);
  }

  equals(other: AST): boolean {…}
}

class Length implements AST {
  constructor(public array: AST) {}

  visit<T>(v: Visitor<T>) {
    return v.visitLength(this);
  }

  equals(other: AST): boolean {…}
}
```

The visitor interface `Visitor<T>` is generic.
That means it can be used to implement passes that return different things.
For example, `Visitor<AST>` produces an `AST` node, `Visitor<void>` can emit code as a side-effect.

Let's convert our existing code generation pass into a visitor.
Since our existing `emit` method returned `void`{.js}, our new visitor will implement `Visitor<void>`.
Instead of having a separate `Environment` class, we make the visitor constructor take all the environment parameters.
In a way, the visitor becomes the environment.

```js
class CodeGenerator implements Visitor<void> {
  constructor(public locals: Map<string, number>,
              public nextLocalOffset: number) {}

  visitAssert(node: Assert) {
    node.condition.visit(this);
    emit(`  cmp r0, #1`);
    emit(`  moveq r0, #'.'`);
    emit(`  movne r0, #'F'`);
    emit(`  bl putchar`);
  }

  visitLength(node: Length) {
    node.array.visit(this);
    emit(`  ldr r0, [r0, #0]`);
  }

  …
}
```

We copy the body of each method, like `Assert.emit` and `Length.emit` into the visitor methods, like `visitAssert` and `visitLength`.

In `emit` methods we used to call `emit` recursively for inner nodes, like this:

```js
  emit(env: Environment): void {
    this.array.emit(env);
    emit(`  ldr r0, [r0, #0]`);
  }
```

Now, instead, we call the `visit` method on them.

```js
  visitLength(node: Length) {
    node.array.visit(this);
    emit(`  ldr r0, [r0, #0]`);
  }
```

Previously `this`{.js} referred to the AST node, but now the node is passed as the parameter called `node`.
Now, `this`{.js} refers to the visitor itself, which we pass instead of the `env` parameter.

In rare places where we created a new environment, we create a new visitor instead with the updated environment.
Here's an example from `visitFunction`.

Before:

```js
    let env = new Environment(locals, -20);
    this.body.emit(env);
```

After:

```js
    let visitor = new CodeGenerator(locals, -20);
    node.body.visit(visitor);
```

As you can see, converting from an AST-based pass to a visitor-based pass is a purely mechanical transformation.
New passes that we will introduce will also be based on the visitor pattern.

<!--- print layout

> **Note:**
>
> If you are using a functional programming language you might notice that the visitor pattern corresponds to pattern matching.

-->


```{=html}
<center><a href="./13-static-type-checking-and-inference">Next: Chapter 13. Static Type Checking and Inference</a></center>
```
