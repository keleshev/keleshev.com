---
title: "8. Second Pass: Code Generation • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 8</small></small><br/>Second Pass: Code Generation<br/><br/></h1>
```

\newpage
\setcounter{page}{112} 
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}    

\chapter{Second Pass: Code Generation}
\includegraphics{chapter-illustrations/8.png}
\newpage

The second and the last pass of our compiler is called the *emitter* or the *code generator*, since it generates the assembly code.
It converts an AST of a program into assembly instrucitons.
How do we organize that?
We extend the `AST` interface with a new method called `emit`.

```js
interface AST {
  emit(): void;
  equals(other: AST): boolean;
}
```

It's a cool method—you may say—it takes no parameters and returns nothing (or `void`{.js}).
So, what's the use of it?
First, it takes the implicit `this`{.js} parameter, and with it all the instance variables of each node.
Second, even though the signature return type is `void`{.js}, when this method is called, it will emit assembly as a *side effect*.
For that we will use an `emit` function (as opposed to a method).
Using this function we can emit instructions like this:

```js
emit("  add r1, r2, r3");
```

More often, we will use template literals for string interpolation when emitting code:

```js
let x = 42;
emit(`  add r1, r2, #${x}`);
```

This will emit `add r1, r2, #42`.
How do we implement the `emit` function?
We can define it so that it appends a line to an array, or writes a line to a file.
But for now, let's define it as follows, for simplicity:

```js
let emit = console.log;
```

That's right, `emit` simply prints to the console's standard output channel.
This is good enough, for now.
We can redirect standard output to a file, and then assemble it.

What about the *method* `emit`?
First, we define this method on every AST node to satisfy the interface.
A dummy implementation will suffice, for a start.
Let's use `Number` node as an example.

\newpage

```js	
class Number implements AST {
  constructor(public value: number) {}

  emit() { throw Error("Not implemented yet"); }

  equals(other: AST) {…}
}
```

Next, we will modify each node to emit the correct assembly.
For example, in case of `Number` it will eventually be as follows:

```js
emit() {
  emit(`  ldr r0, =${this.value}`);
}
```

This way, each AST node will be able to emit corresponding assembly.
Nodes that have other nodes as instance variables will be able to call their `emit` methods.
Note that the order of calls matters.

There's one rule that we will follow: each node, when emitted, will produce assembly code that will put its result into the register `r0`.
This is alredy how function calls work, but we extend it for all nodes that produce a value.
This way, we will know where each value ends up when we emit it.


## Test bench

To test our emitter pass as we develop it, I suggest adding a few temporary AST nodes: `Main` and `Assert`.
As we teach our compiler to emit each kind of node, we want to see the results immediately, not until we can define a somewhat complicated function like `assert`, so we make it into a primitive.
It's the same with `Main`: we want our compiler to produce an entry point to our program before we can define functions.
We define `Main` to take an array of statements.

<!-- It will arrange an entry point and an exit point for them. -->

```js
class Main implements AST {
  constructor(public statements: Array<AST>) {}

  emit() { /* TODO */ }

  equals(other: AST) {…}
}
```

While `Assert` takes a single `condition` on which it will make the assertion:

```js
class Assert implements AST {
  constructor(public condition: AST) {}

  emit() { /* TODO */ }

  equals(other: AST) {…}
}
```

We've left out the `emit` methods for now.

We sligtly modify the `functionStatement` parser to temporarily produce the `Main` node, in case the function name is `main`:

```js
// functionStatement <-
//   FUNCTION ID LEFT_PAREN parameters RIGHT_PAREN
//   blockStatement
let functionStatement: Parser<AST> =
  FUNCTION.and(ID).bind((name) =>
    LEFT_PAREN.and(parameters).bind((parameters) =>
      RIGHT_PAREN.and(blockStatement).bind((block) =>
        constant(
          name === 'main'
            ? new Main(block.statements)
            : new Function(name, parameters, block)))));
```

Same with `Assert`: we produce it inside the `call` parser in case the callee is called `assert`.

```js
// call <- ID LEFT_PAREN args RIGHT_PAREN
let call: Parser<AST> =
  ID.bind((callee) =>
    LEFT_PAREN.and(args.bind((args) =>
      RIGHT_PAREN.and(constant(
        callee === 'assert'
          ? new Assert(args[0])
          : new Call(callee, args))))));
```

As soon as we have enough functionality to define our own functions like `assert`, we'll be able to roll this back.

## Main entry point

Let's imagine how our main entry point should look like in assembly.

```js
.global main
main:
  push {fp, lr}
  …
  mov r0, #0
  pop {fp, pc}
```

As before, we need the `main` label declared as `.global`.
We won't strictly need it until we implement calls, but let's save the `lr` register, so it won't get clobbered eventually, and we can safely return from `main`.
Since we need to align the stack at the double-word boundary, we can push some other register together with `lr`.
We could push `ip` as a dummy, but why not as well push the frame pointer `fp` to get the "classical" function prologue going.
Then we generate the inner statements.
We set the return value to zero, which will be the default return code of the program.
We finish with the "classical" epilogue, where we restore `fp` and by pushing the saved `lr` into `pc` we return from `main` as well.

Now we can implement the `emit` method of `Main`:

```js
class Main implements AST {
  constructor(public statements: Array<AST>) {}

  emit() {
    emit(`.global main`);
    emit(`main:`);
    emit(`  push {fp, lr}`);
    this.statements.forEach((statement) =>
      statement.emit()
    );
    emit(`  mov r0, #0`);
    emit(`  pop {fp, pc}`);
  }

  equals(other: AST) {…}
}
```

\newpage 

Inbetween the prologue and the epilogue, we emit the inner statements in order, using `forEach` loop.
Though, we haven't defined any of the statement nodes that could be emitted here yet.
Nevertheless, our `Main` node is enough to make the first test for our emitter pass: a program that does nothing successfully!

When testing the emitter pass, we could do that in isolation:

```js
new Main([]).emit();
```

Or we could integrate it with the parser:

<!-- TODO

In 8.2 On page 107:
The code "parser.parseStringToCompletion(`function main(){ }`).emit();"
did not run in my implementation, as the final "parser" defined on page
62 always returns a "Block" and at this point we only defined "emit" for
"Main"s.
This happens even with the "function" parser modified according to 8.1.

-->

```js
parser.parseStringToCompletion(`
  function main() {

  }
`).emit();
```

We can pipe the resulting assembly into a file, assemble it and execute it!

<!-- TODO shell commands for this? -->

Congratulations, our compiler has just compiled its first program end-to-end!

## Assert

Like a function call, assert will expect its only argument to be located in the `r0` register.
We compare it with `1` which we treat as a truthy value in our untyped language with no proper booleans.
If equal, we save an ASCII code for dot into `r0` to signify success.
Otherwise, we save the code for `F` to signify failure.
We call `putchar` from `libc` to print it.
We do not terminate the program.

<!-- TODO talk about that our language is unityped/untyped -->

<!-- TODO change truthiness: 0 is false, all else is true -->

```js
  cmp r0, #1
  moveq r0, #'.'
  movne r0, #'F'
  bl putchar
```

To implement the `Assert` node, we just copy-paste this assembly into the `emit` method.
We also make sure to emit the condition, so the result ends up in `r0`.
We don't have any nodes that could be emitted here yet, but that will change quickly.

\newpage

```js
class Assert implements AST {
  constructor(public condition: AST) {}

  emit() {
    this.condition.emit();
    emit(`  cmp r0, #1`);
    emit(`  moveq r0, #'.'`);
    emit(`  movne r0, #'F'`);
    emit(`  bl putchar`);
  }

  equals(other: AST) {…}
}
```

## Number

Let's start with the node for a literal integer.
This way, we can put our `Assert` to use as soon as possible.

We need to load the integer value into `r0`.
We could use `mov` with an immediate, but the range of immediate values is quite restrictive.
That's why we use the `ldr` pseudo-instruction.
As you remember, the assembler will convert it into `mov` with an immediate, if possible.

```js
class Number implements AST {
  constructor(public value: number) {}

  emit() {
    emit(`  ldr r0, =${this.value}`);
  }

  equals(other: AST) {…}
}
```

Now, we can use `Number` in an assertion.

```js
parser.parseStringToCompletion(`
  function main() {
    assert(1);
  }
`).emit();
```

We compile, assemble, and run this program, and we can see that it prints a mighty dot, signifying that the assertion passes.
If you change the integer to 0, you can see the program prints `F`, as it should.

## Negation

Next up is the negation operator!
It is, to some degree, similar to `Assert`.
It takes a single term, that we emit, and compares it to zero.
Depending on that, we move either `1` or `0` into `r0`, thus logically negating the result.

```js
class Not implements AST {
  constructor(public term: AST) {}

  emit() {
    this.term.emit();
    emit(`  cmp r0, #0`);
    emit(`  moveq r0, #1`);
    emit(`  movne r0, #0`);
  }

  equals(other: AST) {…}
}
```


Now we can extend our test program:

```js
function main() {
  assert(1);
  assert(!0);
}
```

<!-- TODO consider allowing !!1 instead of !(!1) -->

From here on, we will skip the boilerplate when we discuss our test program.

## Infix operators

Next up are infix operators: `==`, `!=`, `+`, `-`, `*`, `/` with nodes `Equal`, `NotEqual`, `Add`, `Subtract`, `Multiply`, `Divide`.
All of them are very similar: they take two terms `left` and `right` and operate on them.

Let's use `Add` as an example.

We could emit one node, move the value into a temporary register (say, `r1`), then emit the second node (which value ends up in `r0`) and then sum them up:

```js
class Add implements AST {
  constructor(public left: AST, public right: AST) {}

  emit() { /* First flawed attempt */
    this.left.emit();
    emit(`mov r1, r0`);
    this.right.emit();
    emit(`add r0, r1, r0`);
  }

  equals(other: AST) {…}
}
```

However, this will not work for long: as soon as the `right` node is something more complicated than just a `Number`, emitting it will likely clobber `r1` that stores the `left` result.
This will be the case, for example, if we have two nested infix nodes.
That's why we need to save `r1` onto the stack before emitting `right`, then restore it before we perform the addition:

```js
  emit() { /* Second attempt */
    this.left.emit();
    emit(`push {r0, ip}`);
    this.right.emit();
    emit(`pop {r1, ip}`);
    emit(`add r0, r1, r0`);
  }
```

To maintain 8-byte stack alignment, we also save and restore the dummy `ip` register.
If the `left` node is another nested expression, the pushes and pops will match, and we will be at the same stack pointer location before and after we emit it.

Like in our first attempt, we can avoid using stack in some cases.
We can also do better than waste stack space on saving `ip` each time.
<!-- We will explore it further in *Optimizations* chapter in *Part II*. -->

<!-- TODO Optimizations chapter -->

<!-- TODO contract: stack is the same place after emit -->

All our infix operators will have the same structure: emit right, push, emit left, pop, then the action.
Only the last part will be different.
So, here is a quick table that shows the action part of each infix node.

Table: Action part of each infix node
 
+---------------------+------------------------+
|AST Node             |Emits                   |
+=====================+========================+
|                     |                        |
+---------------------+------------------------+
|                     | ```js                  |
|`Add`                | add r0, r1, r0         |
|                     | ```                    |
+---------------------+------------------------+
|                     |                        |
+---------------------+------------------------+
|                     | ```js                  |
|`Subtract`           | sub r0, r1, r0         |
|                     | ```                    |
+---------------------+------------------------+
|                     |                        |
+---------------------+------------------------+
|                     | ```js                  |
|`Multiply`           | mul r0, r1, r0         |
|                     | ```                    |
+---------------------+------------------------+
|                     |                        |
+---------------------+------------------------+
|                     | ```js                  |
|`Divide`             | udiv r0, r1, r0        |
|                     | ```                    |
+---------------------+------------------------+
|                     |                        |
+---------------------+------------------------+
|                     | ```js                  |
|`Equal`              | cmp r0, r1             |
|                     | moveq r0, #1           |
|                     | movne r0, #0           |
|                     | ```                    |
+---------------------+------------------------+
|                     |                        |
+---------------------+------------------------+
|                     | ```js                  |
|`NotEqual`           | cmp r0, r1             |
|                     | moveq r0, #0           |
|                     | movne r0, #1           |
|                     | ```                    |
+---------------------+------------------------+
|                     |                        |
+---------------------+------------------------+
 
If you want to reduce duplication, you can pull the common part into a new AST node called `Infix`, for example.

In the end, we can add an integration test for infix operators:

```js
function main() {
  assert(1);
  assert(!0);
  assert(42 == 4 + 2 * (12 - 2) + 3 * (5 + 1));
}
```

We are getting somewhere!

## Block statement

Block statement is similar to `Main` but without all the entry point fuss.
It merely emits each statement.

\newpage

```js
class Block implements AST {
  constructor(public statements: Array<AST>) {}

  emit() {
    this.statements.forEach((statement) =>
      statement.emit()
    );
  }

  equals(other: AST) {…}
}
```

Simple test:

```js
function main() {
  assert(1);
  assert(!0);
  assert(42 == 4 + 2 * (12 - 2) + 3 * (5 + 1));
  { /* Testing a block statement */
    assert(1);
    assert(1);
  }
}
```


## Function calls

Next is function calls.
As we learned in the previous chapter, according to the ARM calling convention we need to put the first four arguments into registers `r0`–`r3`, and expect the return value in `r0`.
Let's remind ourselves that the `Call` node holds a `callee` string and an `args` array.

```js
class Call implements AST {
  constructor(public callee: string,
              public args: Array<AST>) {}

  emit() {
    …
  }

  …
}
```

We can start with something simple: calling a function with no arguments.
That's just branching-and-link to the callee label:

```js
  // One argument
  emit(`  bl ${this.callee}`);
```

How about one argument?
If we emit the first argument, it will be in `r0`.
And that's precisely where we need it!
Then we `bl` to it, as previously:

```js
  // Two arguments
  this.args[0].emit();
  emit(`  bl ${this.callee}`);
```

More arguments?
We could have special cases for two, three, and four arguments, and it would also be good for performance reasons, but how about we jump straight to a more general case.
The following will handle two, three, or four arguments.
It was nice not to use any stack space for zero or one arguments.
However, to evaluate more arguments, we need to put them on the stack temporarily.
Otherwise, as we evaluate one, we risk clobbering the value of the other arguments.
Here's how we do it:

```js
  // Up to four arguments
  emit(`  sub sp, sp, #16`);
  this.args.forEach((arg, i) => {
    arg.emit();
    emit(`  str r0, [sp, #${4 * i}]`);
  });
  emit(`  pop {r0, r1, r2, r3}`);
  emit(`  bl ${this.callee}`);
```

First, we allocate enough stack space for up to four arguments, or in other words, 16 bytes.
We do that by subtracting from the stack pointer since the stack grows from higher memory addresses to lower.
Then we loop through arguments using `forEach`, which takes a callback with each item, and optionally its index `i`.
For each argument, we first emit it and then store the result into each stack slot.
We multiply by four to convert array indexes `0`, `1`, `2`, `3` into stack offsets in bytes: `0`, `4`, `8`, `12`.
At this point, the arguments will all be emitted and stored on the stack.
However, we want them to be in registers.
So we `pop` them into the registers in one elegant go.
Now, we've got everything in place so we can branch to the label.

Here's the complete version that combines all three approaches by dispatching on the number of arguments.

```js
class Call implements AST {
  constructor(public callee: string,
              public args: Array<AST>) {}
  emit() {
    let count = this.args.length;
    if (count === 0) {
      emit(`  bl ${this.callee}`);
    } else if (count === 1) {
      this.args[0].emit();
      emit(`  bl ${this.callee}`);
    } else if (count >= 2 && count <= 4) {
      emit(`  sub sp, sp, #16`);
      this.args.forEach((arg, i) => {
        arg.emit();
        emit(`  str r0, [sp, #${4 * i}]`);
      });
      emit(`  pop {r0, r1, r2, r3}`);
      emit(`  bl ${this.callee}`);
    } else {
      throw Error("More than 4 arguments: not supported");
    }
  }

  equals(other: AST) {…}
}
```

We throw an error in the case of more than four arguments, which we don't support in the baseline compiler.

> **Explore**
>
> By specializing code generators for two, three, and four arguments separately (like we did for zero and one argument) you will be able to produce better code (for example, not allocate four slots for two arguments, like we do now).
> From the previous chapter you might have an idea about how to handle more than four arguments.

How do we test this?
We don't yet have a way to define functions.
But we can use some of the `libc` functions to test this.

\newpage

As you remember, `putchar` takes one parameter: let's put it into use by printing the ASCII code for a dot (46), as our test.

There's also a function called `rand` that takes no arguments and returns a random number.
That's not the best function to base our tests on, but we can use it until we can define our own functions.

```js
putchar(46);
assert(rand() != 42);
```

I couldn't find any portable `libc` function that takes two, three, or four integer arguments, so we'll have to wait to test that.

> **Explore**
>
> Modify the parser such that a character literal like `'.'` produces an AST node with the corresponding ASCII code, like `new Number(46)`.
> You can use `string.charCodeAt(index)` method.

## If-statement

Next one is fun: conditional statement, or, in other words, if-statement.
It is fun because we are finally getting to work with control-flow.

Let's look at an example first.
What if we wanted to compile the following if-statement:

```js
if (rand()) {   /* Conditional */
  putchar(46);  /* Consequence */
} else {
  putchar(70);  /* Alternative */
}
```

How would we compile this by hand?
We could start with two labels `ifTrue` and `ifFalse`.
We branch to `ifFalse` if the condition is zero, otherwise to `ifTrue`.
Below each of these labels, we emit the code corresponding to that branch.
In the end, we put an `endIf` label and make sure that both branches jump to it when they reach their end.

<!--Here's what we get:-->
\newpage

```js
  bl rand
  cmp r0, #0
  beq ifFalse
  bne ifTrue

ifTrue:
  ldr r0, =46
  bl putchar
  b endIf

ifFalse:
  ldr r0, =70
  bl putchar
  b endIf

endIf:
  /* Whatever follows next */
```

We can do precisely that, but there are few improvements that we can make, to reduce the number of instructions.
First, the `ifFalse` branch ends with `b endIf` immediately followed by `endIf:` label.
That means we don't have to jump to it since it points to the next instruction anyway.
Similar with `bne ifTrue`, but with one nuance: although this branch is conditional (`ne` suffix), it is in fact not.
Since the two conditions `beq` and `bne` are mutually exclusive, if the execution reached `bne ifTrue` we already know that it will execute.
Furthermore, since `bne ifTrue` is the only use of this label, we can remove `ifTrue` completely.
Here's the resulting code:

```js
  bl rand
  cmp r0, #0
  beq ifFalse

  ldr r0, =46
  bl putchar
  b endIf

ifFalse:
  ldr r0, =70
  bl putchar

endIf:
  /* Whatever follows next */
```

It is shorter, has fewer branches, so it can be executed more efficiently.
But before we jump straight to implementing this in our emitter, we need to solve one problem.
We can't have two different labels called `ifFalse` or `endIf`: labels must be unique.
We need to generate unique labels.

* * *

By convention, labels starting with prefix `.L`, for example, `.L123` are used for code generation.
Let's create a class that will help us generate such labels.

```js
class Label {
  static counter = 0;
  value: number;

  constructor() {
    this.value = Label.counter++;
  }

  toString() {
    return `.L${this.value}`;
  }
}
```

This class has a global `counter` which is incremented each time the constructor is called.
When a `Label` object is created, this counter value is stored in the object's `value` instance variable.
We define a `toString` method that adds the `.L` prefix, so that these objects work well with string interpolation.

* * *

Now we have all things in place to implement the emitter.
We crate two label objects `ifFalseLabel` and `endIfLabel` and use them with string interpolation in the `emit` calls.

```js
class If implements AST {
  constructor(public conditional: AST,
              public consequence: AST,
              public alternative: AST) {}

  emit() {
    let ifFalseLabel = new Label();
    let endIfLabel = new Label();
    this.conditional.emit();
    emit(`  cmp r0, #0`);
    emit(`  beq ${ifFalseLabel}`);
    this.consequence.emit();
    emit(`  b ${endIfLabel}`);
    emit(`${ifFalseLabel}:`);
    this.alternative.emit();
    emit(`${endIfLabel}:`);
  }

  equals(other: AST) {…}
}
```

Now all of our if-statements will have unique labels!

We can throw in a small unit test, for good measure:

```js
if (1) {
  assert(1);
} else {
  assert(0);
}

if (0) {
  assert(0);
} else {
  assert(1);
}
```

## Function definition and variable look-up

It was nice that we could develop and test function calls in isolation, without even being able to define functions.
However, the next two concepts are highly intertwined: function definition and variable look-up.
We already have a special node called `Main` that could be thought of as a function that takes no parameters, and always returns `0`.
We will use it as a template for making our `Function` node's emitter:

\newpage

```js
class Function implements AST {
  constructor(public name: string,
              public parameters: Array<string>,
              public body: AST) {}

  /* First attempt */
  emit() {
    if (this.parameters.length > 4)
      throw Error("More than 4 parameters: not supported");

    emit(``);
    emit(`.global ${this.name}`);
    emit(`${this.name}:`);
    this.emitPrologue();
    this.body.emit();
    this.emitEpilogue();
  }

  emitPrologue() {
    emit(`  push {fp, lr}`);
    emit(`  mov fp, sp`);
    emit(`  push {r0, r1, r2, r3}`);
  }

  emitEpilogue() {
    emit(`  mov sp, fp`);
    emit(`  mov r0, #0`);
    emit(`  pop {fp, pc}`);
  }

  equals() {…}
}
```

Similar to `Call` we will limit ourselves to four parameters this time.
We make a guard to enforce this and raise an error otherwise.
We start by emitting an empty line to separate assembly functions for readability.
Similarly to `Main`, we emit the `.global` directive and the label.
However, this time we don't hardcode it to `main`, but use the name of the function instead, using string interpolation.

Here the function prologue starts.
We have split the function prologue and epilogue into its own methods for readability.
This is not something that we have done before.

Let's look at the prologue, first.
We save the frame pointer and the link registers, and we set our new frame pointer.
We expect our parameters to be in registers `r0`–`r3`.
However, as soon as we start emitting the body of the function, we risk clobbering them, so we need to save them on the stack.
Fortunately, ARM allows us to do it with a single `push` instruction.
(An optimizing compiler would make an analysis called register allocation to determine which parameters can be kept in registers.)

Next, we emit the body of the function, which is followed by the function epilogue.
Here we undo the effect of the function prologue: by setting the stack pointer value to frame pointer value we effectively deallocate whatever stack space we allocated (in the prologue, or otherwise).
We set `r0` and thus our return value to `0`.
This is to mimic the fact that JavaScript functions return `undefined`{.js} when there's no explicit return.
We pick `0` because it is falsy, like `undefined`{.js}.
This also removes the risk of returning a garbage value that was a leftover of some computation, in case we forget to have a `return`{.js} statement.
As the last instruction, we restore the caller's frame pointer and pop the saved link register into the program counter, effectively returning from the function.

> **Explore**
>
> We pushed four registers onto the stack.
> An improvement could be to specialize this code to handle the cases with fewer parameters more efficiently.
> If you do that, don't forget about 8-byte stack alignment.

So far, so good.
Now, how do we access those parameters in the body of the function?
They are located at well-known offsets from the frame pointer.
Since the stack grows from high addresses to low, we know that we can access parameters using negative offsets relative to the frame pointer.
We also know that `push {r0, r1, r2, r3}` pushes the registers in the reverse order, same as this equivalent (but bulkier) code:

```js
  push {r3}
  push {r2}
  push {r1}
  push {r0}
```

That means that the fourth parameter (from register `r3`) will be stored at the location `fp - 4`, third (`r2`) at `fp - 8`, second (`r1`) at `fp - 12`, first at `fp - 16`.

So, when we encounter an identifier that refers to one of the parameters, all we need to know is the offset from the frame pointer to locate its value.
We can load it with `ldr`.
Here's an example of loading the first parameter:

```js
  ldr r0, [fp, #-16]
```

What we can do is to store the mapping from parameter name to an offset from the frame pointer and make sure it is passed down to all emitters.
That means that whenever we encounter an identifier node `Id` we can look up the offset in that mapping and then we will know how to load it.
This mapping is usually called an *environment*.

We could just pass around a `Map<string, number>`, but my crystal ball tells me that we will need to extend this data structure in the near future.
So, instead we will introduce a data class with this map as an instance variable called `locals`:

```js
class Environment {
  /* Initial version */
  constructor(public locals: Map<string, number>) {}
}
```

We call this class `Environment`.
Right now it only contains the `locals` map, which is the environment for our local variables, but it could include other environments, such as global variable environment, or type environments, or an environment with function signatures.
We called our map `locals` and not `parameters`, because we foresee that we will use it for other local variables, and not just for function parameters.
<!--It often grows to hold much more, and then a good name for it could be a more general `Context`.-->

<!--
In the `Environment` constructor, we make the `locals` parameter optional with the default value being an empty map.
This is a mutable map, which we will modify.
Fortunately, JavaScript default values are evaluated on each call so that we will get a new mutable map each time.
But this is not the case in some of the other languages.
-->

Now, there is a hefty change that we need to make.
We need to adjust the `AST` interface to take the new `Environment` parameter, which we will pass to `emit`.
We will consistently call this parameter `env`.

```js
interface AST {
  emit(env: Environment): void;
  equals(other: AST): boolean;
}
```

This will also require us to modify all AST nodes to take this environment and pass it down to all other node emitters.
This is a very invasive, but mechanical change.
We'll not go through all the nodes for this, let's just use `Add` as our example.

```js
class Add implements AST {
  constructor(public left: AST,
              public right: AST) {}

  emit(env: Environment) {
    this.left.emit(env);
    emit(`  push {r0, ip}`);
    this.right.emit(env);
    emit(`  pop {r1, ip}`);
    emit(`  add r0, r1, r0`);
  }

  equals(other: AST) {…}
}
```

The emitter now takes an `env` parameter, which it passes down to both its child AST nodes: `left` and `right`, in this case.

Now, back to our `Function`.
We need to modify it to fulfil the new `AST` interface with `Environment`.
However, we will ignore the incoming environment since we will not support nested functions.
We will bind it to an underscore to signify to the reader of this code that this variable is not used on purpose.
Here's our new take on function definition:

```js
class Function implements AST {
  …

  /* Second attempt */
  emit(_: Environment) {
    if (this.parameters.length > 4)
      throw Error("More than 4 parameters: not supported");

    emit(``);
    emit(`.global ${this.name}`);
    emit(`${this.name}:`);
    this.emitPrologue();
    let env = this.setUpEnvironment();
    this.body.emit(env);
    this.emitEpilogue();
  }
```

\newpage

```js
  setUpEnvironment() {
    let locals = new Map();
    this.parameters.forEach((parameter, i) => {
      locals.set(parameter, 4 * i - 16);
    });
    return new Environment(locals);
  }
}
```

Here, in the function definition node, we know both the names of the parameters and the offsets at which they will be stored.
So this is the ideal place to create a new environment.
We do that in a method called `setUpEnvironment`.
First, we create an empty environment, and then we loop through the parameters using `forEach` and set the locals map for each parameter to its offset relative to the frame pointer.
Here, `forEach` passes not only items but also (optionally) each item's index `i`.
To map each index to its frame pointer offset we multiply the index by four to convert from words to bytes, and remove `16` since this is how many bytes we had allocated on the stack when we popped the four parameters in the prologue.
We pass the constructed environment when emitting the body, which, in turn, will pass it to all its children, and so forth.

Now, a node that needs to access a local parameter can look it up in the environment.
And what node could it be if not `Id`, the node for the identifiers in our code?
All the hard work is done in the `Function` node, so our `Id` node will be quite simple:

```js
class Id implements AST {
  constructor(public value: string) {}

  emit(env: Environment) {
    let offset = env.locals.get(this.value);
    if (offset) {
      emit(`  ldr r0, [fp, #${offset}]`);
    } else {
      throw Error(`Undefined variable: ${this.value}`);
    }
  }

  equals() {…}
}
```

\newpage

It looks up the offset from the local environment by identifier name.
If the name is not in the environment, it throws an error.
This means that a variable was used before it is defined.
Otherwise, it loads the value using `ldr` relative to the frame pointer.

These frame pointers are handy, aren't they?

Now that we have implemented functions with parameters, we can implement quite a few interesting ones!
First, we can get rid of the `Main` node, and generate the `main` function just like any other.
Second, we can get rid of our `Assert` primitive, and implement it instead as a function:

```js
function assert(x) {
  if (x) {
    putchar(46);
  } else {
    putchar(70);
  }
}
```

Finally, it's good to test that we got parameter passing right.
Here's one of such tests:

```js
function assert1234(a, b, c, d) {
  assert(a == 1);
  assert(b == 2);
  assert(c == 3);
  assert(d == 4);
}
```

It could be called as `assert1234(1, 2, 3, 4)` from `main`.

It feels like we can implement almost anything now; however, one critical piece is still missing.

## Return

Functions must be able to return values.
Even fans of continuation-passing style would agree.
And thanks to frame pointers, implementing the `Return` node is easy:

\newpage

<!-- TODO consistently order epilogue instructions: Main, Return, FD -->
<!-- TODO check equals function signature in the book for `other` param -->

```js
class Return implements AST {
  constructor(public term: AST) {}

  emit(env) {
    this.term.emit(env);
    emit(`  mov sp, fp`);
    emit(`  pop {fp, pc}`);
  }

  equals(other: AST) {…}
}
```

We only need to emit the node (which is returned) into `r0`, and then repeat the same instructions as in the epilogue.

Now, the language of our compiler is technically-speaking Turing-complete.
Loops, you say?
We can loop using recursion, which we get for free since our functions are using the stack.
(We are not getting tail-call optimization for free, though).
This step warrants extensive testing, but the one test I have in mind is this:

```js
function factorial(n) {
  if (n == 0) {
    return 1;
  } else {
    return n * factorial(n - 1);
  }
}
```

The factorial function!
We can call it from `main` as follows:

```js
assert(factorial(5) == 120);
```

It's a small dot for a test suite, but a giant leap for our compiler!

* * *

We've got all the essentials in place now.
We will finish this chapter with a couple of niceties: local variables, assignments, and while loops.
As a treat.

## Local variables

Here we will set out to implement local variables, as declared with `var`{.js} keyword in JavaScript and represented as `Var` node in our AST.

Why `var`{.js} and not `let`{.js}?
We have used only `let`{.js} in the implementation of this compiler!

Let's remind ourselves of the difference.
Here's a function using `let`{.js}:

```js
function f() {
  let x = 1;
  {
    let x = 2;
  }
  console.log(x);
}
```

And the same one using `var`{.js}:

```js
function f() {
  var x = 1;
  {
    var x = 2;
  }
  console.log(x);
}
```

The first one prints `1`, and the second one prints `2`.
The difference is that the `var`{.js} bindings work at the function scope, and `let`{.js} bindings work at the block scope.
So the two "vars" refer to the same variables, but the two "lets" are different: the second one is within another scope delimited by braces.

The reason we implement `var`{.js} is that it simplifies scope handling: you only need one scope per function.
That's probably also the reason JavaScript introduced `var`{.js} first, and `let`{.js} much later.
There's also `const`{.js}, which is just like `let`{.js}, but makes the assignment forbidden on its bindings.

So, how do we implement `var`{.js}?
We can push the value on the stack, then look it up in the environment, just like with parameters.
However, when defining parameters, we know their offset: they are at the beginning of the frame.
However, when we emit a `var`{.js}, we don't know how far down the stack we currently are.
But we can track this in the environment!

Let's modify the `Environment` class to store the `nextLocalOffset` number, which represents the next available frame pointer offset.
This is also sometimes called a *stack index*.

```js
class Environment {
  constructor(public locals: Map<string, number>,
              public nextLocalOffset: number) {}
}
```

For starters, we could initialize it to `0`.
However, in `Function` we need to set it up depending on how many parameters we allocate.
Right now we always allocate four, at offsets `-4`, `-8`, `-12`, and `-16`.
So the next available offset is `-20`.
And that's the value that we use in the environment setup:

```js
class Function implements AST {
  …
  setUpEnvironment() {
    let locals = new Map();
    this.parameters.forEach((parameter, i) => {
      locals.set(parameter, 4 * i - 16);
    });
    nextLocalOffset = -20;
    return new Environment(locals, nextLocalOffset);
  }
  …
}
```

Now, onto the `Var` node.
Theoretically, we could add the variable name to the `local` environment mapping, so it maps to the `nextLocalOffset` value, then push the value onto the stack, and update the `nextLocalOffset` to point to the next available offset.
However, we need to maintain 8-byte alignment, so it is slightly more involved:

```js
class Var implements AST {
  constructor(public name: string,
              public value: AST) {}

  emit(env: Environment) {
    this.value.emit(env);
    emit(`  push {r0, ip}`);
    env.locals.set(this.name, env.nextLocalOffset - 4);
    env.nextLocalOffset -= 8;
  }

  equals(other: AST) {…}
}
```

We still start by emitting the value and pushing it onto the stack, but we also need to push something like an `ip` register to keep the stack 8-byte aligned.
This way it's the `ip` that will be located at the `nextLocalOffset`, so when updating the local environment, we subtract another `4` bytes from it.
Now, we need to advance `nextLocalOffset` two stack slots ahead; in other words, we decrement it by `8`.


> **Explore**
>
> This wastes 50% of the stack space for locals.
> Here's a way to fix it: you can add an array of offsets `vacantOffsets` to the `Environment`.
> Then each time you need a stack slot you first check if there are any vacant slots, and try to use it (and remove it from the array).
> And only if there are no such slots, you allocate new stack space.
> This technique can also be used to take advantage of over-allocating in other situations, for example, when you have an odd number of function parameters.
> There's also a way to organize it all neatly into a `Frame` data structure that handles this offset twiddling in one place, so every relevant emitter doesn't have to keep track of the offset math.

Let's add an assertion to test our `var` handling:

```js
var x = 4 + 2 * (12 - 2);
var y = 3 * (5 + 1);
var z = x + y;
assert(z == 42);
```

## Assignment

Assignment handling is very similar to identifier look-up.
Except instead of reading its value, we are writing it.
We emit the value into `r0`.
Then we look up the frame pointer offset in the local environment.
If the environment look-up fails, we throw an error: that variable was not defined at this point of time.
Otherwise, we use the `str` instruction to store the value from `r0` into the frame pointer offset.

\newpage

```js
class Assign implements AST {
  constructor(public name: string,
              public value: AST) {}

  emit(env: Environment) {
    this.value.emit(env);
    let offset = env.locals.get(this.name);
    if (offset) {
      emit(`  str r0, [fp, #${offset}]`);
    } else {
      throw Error(`Undefined variable: ${this.name}`);
    }
  }

  equals(other: AST) {…}
}
```

A simple test for the assignment:

```js
var a = 1;
assert(a == 1);
a = 0;
assert(a == 0);
```

> **Explore**
>
> Implement `const`{.js} bindings similar to `var`{.js}, but such that assignment is not allowed on them.
> A way to do that would be to change the locals mapping to include not only an offset but also a flag that signifies whether the binding is constant or not.
> Then, when the assignment looks it up, check that the constant flag is not set, and fail otherwise.

## While-loop

While-loop handling is in many ways similar to the `If` statement handling.
It has a conditional expression, which is checked for truthiness, but it has only one branch.
The other difference is that at the end of that branch, it jumps back to the beginning.

\newpage

```js
class While implements AST {
  constructor(public conditional: AST,
              public body: AST) {}

  emit(env: Environment) {
    let loopStart = new Label();
    let loopEnd = new Label();

    emit(`${loopStart}:`);
    this.conditional.emit(env);
    emit(`  cmp r0, #0`);
    emit(`  beq ${loopEnd}`);
    this.body.emit(env);
    emit(`  b ${loopStart}`);
    emit(`${loopEnd}:`);
  }

  equals(other: AST) {…}
}
```

Here we generate two unique labels: `loopStart` and `loopEnd`.
We check the conditional and branch off to `loopEnd` if it is falsy.
Then follows the body of the loop.
In the end, we unconditionally branch to the `loopStart` label.
A quick test for the `while`{.js} loop may look like this:

```js
var i = 0;
while (i != 3) {
  i = i + 1;
}
assert(i == 3);
```

We've put away the `while`{.js} loop handling for so long because to test it we first need the assignment to work.  We can now also implement a version of the `factorial` function using the `while`{.js} loop:

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

> **Explore**
>
> How do you implement a `for`{.js} loop?
> A `for`{.js} loop can be thought of as a special case of the `while`{.js} loop.
> Consider that the following `for`{.js} loop:
>
> ```js
> for (i = 1; i < 5; i = i + 1) {
>   body();
> }
> ```
>
> Is equivalent to this `while`{.js} loop:
>
> ```js
> i = 1;
> while (i < 5) {
>   i = i + 1;
>   body();
> }
> ```

 * * *

The baseline compiler is done.
Now, onto *Part II*, where we will continue extending and expanding the compiler with new functionality.

```{=html}
<center><a href="./09-introduction-to-part-2#fold">Next: Chapter 9. Introduction to Part II</a></center>
```
