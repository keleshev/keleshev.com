---
title: "10. Primitive Scalar Data Types • Compiling to Assembly from Scratch"
---

```{=html}
<header>
<h1><small><small>Chapter 10</small></small><br/>Primitive Scalar Data Types</h1>
<a href='./#table-of-contents'>Compiling to Assembly from Scratch</a>
<br/>by <a href='/'>Vladimir Keleshev</a>
</header>
```

\newpage
\setcounter{page}{146}
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}  


\chapter{Primitive Scalar Data Types}
\includegraphics{chapter-illustrations/10.png}
\newpage


When we say *scalar data types* we mean data types that fit into a single machine word, which is not a pointer but carries a value in itself.
We already have one scalar data type for integer numbers.

Let's introduce a boolean data type.
First, we need an AST node for it:

```js
class Boolean implements AST {
  constructor(public value: boolean) {}

  emit(env: Environment) {
    if (this.value) {
      emit(`  mov r0, #1`);
    } else {
      emit(`  mov r0, #0`);
    }
  }

  equals(other: AST): boolean {…}
}
```

We emit it the same way as integers 1 and 0 (for `true`{.js} and `false`{.js}).

In the parser, we introduce new tokens for `true`{.js} and `false`{.js}, and compose them to create a `boolean`{.js} parser:

```js
let TRUE =
  token(/true\b/y).map((_) => new Boolean(true));
let FALSE =
  token(/false\b/y).map((_) => new Boolean(false));

let boolean: Parser<AST> = TRUE.or(FALSE)
```

We can extend the `atom` rule of the expression grammar by adding a `boolean` alternative.
A good idea at this point is to introduce an additional `scalar` rule:

```js
scalar <- boolean / ID / NUMBER
atom <- call / scalar / LEFT_PAREN expression RIGHT_PAREN
```

Then, after implementing this grammar as a parser we get booleans in our extended baseline language:

```js
assert(true);
assert(!false);
```

However, they behave exactly like integers `1` and `0`, so `assert(true == 1)`{.js} will succeed.
Under static typing, this comparison would be rejected by the compiler.
Under dynamic typing, this would evaluate to `false`{.js} at run-time.

 * * *

Similarly, we can add other scalars, such as `undefined`{.js}, `null`{.js} (that compile to 0, like `false`{.js}), or a character type, which could compile to the integer value of its ASCII code (though, JavaScript and TypeScript treat characters as strings).

Table: Summary of AST constructor signatures with examples

+---------------------------------------------------------------+------------------+
| AST Constructor Signature                                     | Example          |
+===============================================================+==================+
| `Boolean(value: boolean)`{.js}                                | `true`{.js}      |
|                                                               |                  |
| `Undefined()`                                                 | `undefined`{.js} |
|                                                               |                  |
| `Null()`                                                      | `null`{.js}      |
+---------------------------------------------------------------+------------------+
                                                                                   
```{=html}
<center><p><a href="./11-arrays-and-heap-allocation">Next: Chapter 11. Arrays and Heap Allocation</a></p></center>
```
