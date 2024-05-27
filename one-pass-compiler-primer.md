---
title: One-pass Compiler Primer
fancy-title: "One-pass Compiler<br/><small><small>Primer</small></small>"
date: 2020-05-21
cta: {book: yes}
---


Let's look at what is a one-pass compiler and try to implement one.

<!--So instead of parsing the source into AST and then traversing it to emit code, a compiler would emit code during parsing. -->


A one-pass compiler emits assembly (or binary code) right during parsing, without creating an intermediate representation, such as an AST.
This is a rare technique that was used back in the days when computer memory was scarce.
This limited both the language features that were possible and the quality of the produced code.
But this techniques produced fast compilers that made Bill Gates envy.

<!--When it comes to langauge features, the most straightforward outcome of having a one-pass compiler is that forward references are not possible.

It also limits the kinds of optimizations that the compiler can do.-->


## Turbo Pascal


A notable example of a one-pass compiler is Turbo Pascal.


Fast compilation speed that the one-pass compiler architecture enabled is often cited as the decisive factor in the success of Turbo Pascal.

*From [Wikipedia](https://en.wikipedia.org/wiki/Turbo_Pascal):*

> Bill Gates saw the success of Turbo Pascal
> "in very personal terms, and 'couldn't understand why
> [Microsoft's] stuff was so slow.
> He would bring in Greg Whitten
> [programming director of Microsoft languages]
> and yell at him for half an hour.'
> He couldn't understand why Kahn had been able to
> beat an established competitor like Microsoft".


## Compiler

Let's make a simple one-pass compiler.
Not for a whole programming language, but just for simple arithmetic expressions, like the following:

<center><code>4 + 2 * 10 + 3 * (5 + 1)</code></center>



We'll target x86-64 and will use [flex](https://en.wikipedia.org/wiki/Flex_(lexical_analyser_generator)) and [bison](https://en.wikipedia.org/wiki/GNU_Bison) for generating
our lexer and parser, respectively.
I've used the Wikipedia bison example as an inspiration.

We start with defining our token type in the "yacc" file:

```yacc
%token TOKEN_LPAREN "("
%token TOKEN_RPAREN ")"
%token TOKEN_PLUS   "+"
%token TOKEN_STAR   "*"
%token <int> TOKEN_NUMBER "number"
```

Then we go onto defining our simple lexer in the "lex" file:

```c
[ \r\n\t]*  { continue; /* Skip blanks. */ }
[0-9]+      { sscanf(yytext, "%d", &yylval->value);
              return TOKEN_NUMBER; }
"*"         { return TOKEN_STAR; }
"+"         { return TOKEN_PLUS; }
"("         { return TOKEN_LPAREN; }
")"         { return TOKEN_RPAREN; }
.           { continue; /* Skip unexpected characters. */ }
```

And now, the grammar for our expression language.
Let's leave out the semantic actions, for now.

```yacc
input:
  expr

expr:
    "number"
  | expr "+" expr
  | expr "*" expr
  | "(" expr ")"
```

Above the grammar we specify the operators in order of increasing precedence:

```yacc
%left "+"
%left "*"
```

They are both left-associative:
2 + 3 + 4 means ((2 + 3) + 4).
This is not a very important
property for addition and multiplication, since the operations themselves are associative.

We need to directly emit some assembly code in each semantic action that we add to our grammar.
We can get fancier later if we need to, but for now, let's define our emit function as an alias to `printf`.

```c
#define emit printf
```

Thus, we'll spit assembly instructions directly to the standard output channel, which we can pipe to a file if needed.

And now, onto the semantic actions.
Each time we encounter a number, we push it onto the stack:

```yacc
    "number" { emit("  push $%d\n", $1); }
```

The order of when each semantic action is firing matters.
So, when we encounter an operation, like addition,
the two inner expressions have already been emitted.
Thus, we can expect their values to be at the top of the stack.
What we can do is, pop the values into some registers,
perform the addition (in this case), and push the resulting value back onto the stack:

```yacc
  | expr "+" expr  { emit("  pop %%rax\n");
                     emit("  pop %%rbx\n");
                     emit("  add %%rbx, %%rax\n");
                     emit("  push %%rax\n"); }
```

We need to use double percent signs for registers since this is a `printf` format string.

We do the same for multiplication, except that the accumulator register `%rax` is an implicit parameter of the `mul` instruction.

```yacc
  | expr "*" expr  { emit("  pop %%rax\n");
                     emit("  pop %%rbx\n");
                     emit("  mul %%rbx\n");
                     emit("  push %%rax\n"); }
```

What do we do when we encounter parenthesis?
We do nothing, since the inner expression is already emitted.

```yacc
  | "(" expr ")"   { /* No action. */ }
```

Now, we can generate assembly snippets given an arithmetic expression.
However, a bunch of pushes and pops don't make for a complete assembly listing.
We need a `main` (assuming we link to `libc`) or a `_start`.

We can use a [mid-rule](https://www.gnu.org/software/bison/manual/html_node/Mid_002dRule-Actions.html) semantic action to generate our `main` label:

```yacc
  input:
                     { emit(".global main\n");
                       emit("main:\n"); }
    expr             { emit("  pop %%rax\n");
                       emit("  ret\n"); }
```

As the final semantic action, we pop the only expected value and return it from `main` as the exit code of our program.

Now, if we feed this parser our original expression:

<center><code>4 + 2 &#42; 10 + 3 &#42; (5 + 1)</code></center>

It will emit the following assembly listing:

```
.global main
main:
  push $4
  push $2
  push $10
  pop %rax
  pop %rbx
  mul %rbx
  push %rax
  pop %rax
  pop %rbx
  add %rbx, %rax
  push %rax
  push $3
  push $5
  push $1
  pop %rax
  pop %rbx
  add %rbx, %rax
  push %rax
  pop %rax
  pop %rbx
  mul %rbx
  push %rax
  pop %rax
  pop %rbx
  add %rbx, %rax
  push %rax
  pop %rax
  ret
```

If we pipe it into a file called `test.s`, assemble it and execute it, the program will produce no output, however, we can check the exit code:

```bash
$ cc test.s -o test
$ ./test
$ echo $?
42
```

Which is the result of our arithmetic expression!

This is pretty much all we can cover in a short blog post.


I can imagine implementing variables by pushing their values onto the stack and remembering their stack offsets in a hash table… Something similar for functions' signatures… It looks like a lot of global mutable state is needed for a one-pass compiler to work.


How do you optimize something like this?
An optimizing compiler would constant-fold our expression into a single number ahead of time. Still, in one-pass case you only get a very myopic view of the code.

<!--The outcome of this experiment, I guess, is, don't make a
one-pass compiler?!-->

<!--
<center>⁂</center>

This blog post was inspired by a [question on Quora](https://www.quora.com/What-is-Single-Pass-Compiler-and-its-example/answer/Vladimir-Keleshev-1).
-->

## The Code

The complete code, including lexer, parser, and a makefile is available on GitHub [as a gist](https://gist.github.com/keleshev/cdd6d3d46437284b2a0c2fc42cf90e0f).
[☰](/ "Home")

## Citation

<small>
```       
@misc{Keleshev:2020-5,
  title="One-pass Compiler Primer",
  author="Vladimir Keleshev",
  year=2020,
  howpublished=
    "\url{https://keleshev.com/one-pass-compiler-primer}",
}
```
</small>

* * *

*Did you know, I worte a book about compilers?
Unfortunately, the compiler described in the book is not one-pass.
I know, right?
But it's a two-pass compiler that produces ARM assembly code.
The book even teaches you enough assembly programming to get going.
The examples are written in TypeScript, but it can be followed in any language, so check it out!*
<br/>
<br/>


