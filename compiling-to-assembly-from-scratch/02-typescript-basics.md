---
title: "2. TypeScript Basics • Compiling to Assembly from Scratch"
---

```{=html}
<header>
<h1><small><small>Chapter 2</small></small><br/>TypeScript Basics</h1>
<a href='./#table-of-contents'>Compiling to Assembly from Scratch</a>
<br/>by <a href='/'>Vladimir Keleshev</a>
</header>
```

\chapter{TypeScript Basics}
\includegraphics{chapter-illustrations/2.png}
\newpage

<!-- TODO? Example of `every` -->

This chapter gets you up-to-speed with TypeScript.
Feel free to skip it if you already know it.

TypeScript is designed to be a *superset* (or an extension) to JavaScript that adds type annotations and type checking.
So, apart from the type annotations, it is just modern-day JavaScript.

Let's get going.
First, `console.log` prints a message to the console:

```js
console.log("Hello, world!");
```

Strings use double or single quotes.
Strings written with back-ticks are called *template literals*.
They can be multiline, *and* they can be interpolated (or injected with expressions), like in a template:

```js
console.log(`2 + 2 = ${2 + 2}`); // Prints: 2 + 2 = 4
```

Next, `console.assert` is a quick and portable way to test something, if you don't have a testing framework at hand:

```js
console.assert(2 === 2); // Does nothing
console.assert(0 === 2); // Raises an exception
```

Triple equals `===` is strict (or exact) equality, while double equals `==` is loose equality.
Similarly with `!==` and `!=`.
For example, with loose equality `true` equals to `1`, but with strict equality they are not equal.
We will only use strict equality in the compiler code, but in the basline language we will use `==` and `!=` operators.

To abnormally terminate a program, you can throw an exception:

```js
throw Error("Error message goes here.");
```

It is a good practice to define your own exceptions, but for brevity, we'll use built-in exceptions in this book.

Functions can be defined using the `function`{.js} keyword:

```js
function add(a: number, b: number) {
  return a + b;
}
```

In many cases, type annotations are optional in TypeScript.
However, they are necessary for most function (and method) parameters.
So far, we were describing features that are just plain JavaScript.
However, here we've got a function that has a *type annotation*.
The types of the parameters are *annotated* as `number`.

Another way to define a function is by writing a so-called *arrow function*, (which is also called an *anonymous function*, or a *lambda function*):

```js
let add = (a, b) => a + b;
```

Next up are variables. They come in several forms in TypeScript (and JavaScript).
Variables are bound with `var`{.js}, `let`{.js} (and `const`{.js}).
While `var`{.js} scope is at the function (or method) level,
`let`{.js} scope is delimited with braces.

Compare `var`{.js}:

```js
function f() {
  var x = 1;
  {
    var x = 2;
  }
  console.log(x); // Prints 2
}
```

With `let`{.js}:

```js
function f() {
  let x = 1;
  {
    let x = 2;
  }
  console.log(x); // Prints 1
}
```

We'll only be using `let`{.js} in the compiler code, however, `var`{.js} needs mentioning because it is `var`{.js} that we will implement for the baseline language.

Although mostly optional, bindings can be type-annotated:

```js
let a: Array<number> = [1, 2, 3];
```

Here, `Array<number>` means an array of numbers.

TypeScript, like JavaScript, allows for literal regular expressions.
While strings are delimited with quotes, literal regular expressions are delimited with forward slashes:

```js
let result = "hello world".match(/[a-z]+/);
console.assert(result[0] === "hello");
```

\newpage

Classes are the go-to way for creating custom data types in TypeScript.
Here's a simple data class:

```js
class Pair {
  public first: number;
  public second: number;

  constructor(first: number, second: number) {
    this.first = first;
    this.second = second;
  }
}
```

You create a new object using the `new`{.js} keyword:

```js
let origin = new Pair(0, 0);
```

TypeScript has a shortcut for defining simple data classes like this, where constructor parameters are immediately assigned as instance variables:

```js
class Pair {
  constructor(public first: number,
              public second: number) {}
}
```

Note how the `public`{.js} keyword is specified in the parameter list.
This is exactly equivalent to the previous definition.
We will use this shortcut a lot in this book.

We will also define some classes that can clash with the built-in ones, like `Boolean` and `Number`.
To avoid that, make sure to define them at the module scope and not at the global scope.
The simplest way to acheive that is to make sure to add an empty
`\VERB|\KeywordTok{export }|`{=tex}`<code><b>export </b></code>`{=html}`{}`
to your source file.
Using 
`<code><b>import</b></code>`{=html}
`\VERB|\textbf{import}|`{=tex}
or
`<code><b>export</b></code>`{=html}
`\VERB|\textbf{export}|`{=tex}
keywords changes the file scope from global to module scope.

Next is a more extensive example, with static variable `zero`, static method `origin`, and an instance method `toString`.
Remember that static variables and static methods are just global variables and global methods that are namespaced by the class name.

\newpage

```js
class Pair {
  static zero = 0;

  static origin() {
    return new Pair(0, 0);
  }

  constructor(public first: number,
              public second: number) {}

  toString() {
    return `(${this.first}, ${this.second})`;
  }
}
```

You might find that some of the whitespace and formatting choices look odd in this book.
This is because the code listings are optimized for compactness, which is important for a print book.

* * *

There's much more to TypeScript, but we will, for the most part, limit ourselves to the subset described here.

\section{PUSH TOC ONE LINE DOWN}


```{=html}
<center><a href="./03-high-level-compiler-overview">Next: Chapter 3. High-level Compiler Overview</a></center>
```
