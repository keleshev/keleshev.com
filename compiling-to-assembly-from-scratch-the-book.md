---
title: Compiling to Assembly from Scratch
---

<br/>
<center><img src=./dragon.jpg width=168 height=228 /></center>

Compiling to Assembly<br/><small>from Scratch<br/><small><em></em></small></small>
==================================

<title>Compiling to Assembly from Scratch — Vladimir Keleshev</title>

<center>— the book —<br/>



<em>ETA: Summer 2020</em></center>




<big>*So, you've been trying to learn how compilers and programming languages work?* </big>

Perhaps, you've learned about compiling to JavaScript,
or about building an interpreter? Or, maybe, about
compiling to bytecode? All good steps.

*But there's a tension building up.*

Because it feels a bit like cheating.
Because you know that somewhere, somehow, the code you write
is translated to assembly instructions. To the machine language.
That's where the rubber hits the road. That's where it gets hot.
And, oh-so-many resources are hesitant to cover this part.
But not this book.

<big>
This *small* book will show you in detail
how you can build a compiler from scratch
that goes all the way from *source* to *assembly*.
</big>

The example code is written in **TypeScript**, a dialect of **JavaScript**.
The book describes the design and implementation of a compiler that emits
32-bit **ARM** assembly instructions.

## Why ARM?

In many ways, the ARM instruction set is what makes this book possible.

Compared to Intel x86-64, the ARM instruction set is a work of art.

Intel x86-64 is the result of evolution from an 8-bit processor,
to a 16-bit one, then to a 32-bit one, and finally to a 64-bit one.
At each step of the evolution, it accumulated complexity and cruft.
At each step, it tried to satisfy conflicting requirements.

* Intel x86-64 is based on *Complex Instruction Set Architecture* (CISC),
which was initially optimized for writing assembly by hand.
* ARM, on the other hand, is based on *Reduced Instruction Set Architecture* (RISC),
which is optimized for writing compilers.

*Guess which one is an easier target for a compiler?*

If this book targeted Intel x86-64 instead of ARM, it would have been three times as long
and&hairsp;—&hairsp;more likely&hairsp;—&hairsp;never written.
Also, with 160 *billion* devices shipped, we better get used to the fact
that ARM is the dominant instruction set architecture today.

In other words… ARM is a good start.
After learning it, you will be better equipped
for moving to x86-64 or the new ARM64.

*Will you be able to run the code your compiler produces?*

I bet you will! The Appendix will contain a bazillion ways
to execute ARM code, starting from Raspberry Pi,
could VM, to various ways to emulate ARM on Linux, Windows, and macOS.

## Why TypeScript?

First of all, you will be able to follow this book in any reasonable programming language.
For me, it was tough to pick one for this job, and I'm pleased I've chosen TypeScript.

TypeScript is probably nobody's favorite, but it's a good compromise:

* Are you coming from a dynamic language like JavaScript, Python, or Ruby?
  Then if you close your eyes at the
  type annotations, TypeScript is just modern-day JavaScript.
* If you're coming from Java or C#, then you will feel right at home,
  since TypeScript
  is brought to you by the same people who brought you C# *(and Turbo Pascal!)*.

Don't worry if you've never seen TypeScript code before.
If you can read the following, you will most likely be able to pick it up,
as the book goes *(real code from the book here!)*:

```js
class Label {
  static counter = 0;
  value: number; // Type annotation

  constructor() {
    this.value = Label.counter++;
  }

  toString() {
    return '.L' + this.value;
  }
}
```

I avoided using any TypeScript- or JavaScript-specific
language features in the code.

If you're into statically-typed functional programming
languages (Haskell, OCaml, or Reason ML),
you will find that the class structure I used
has a nice translation to an algebraic data type.
It is, in fact, how I wrote it first.


<style>
  #home { float: left; }
  pre {
    border-left: 0;
    font-size: 16px;
    line-height: 1.5em;
  }

</style>

## The Contents


The book consists of two parts. Part I
presents a *detailed*, *step-by-step* guide on how
to develop a small "baseline" compiler that can compile simple
programs to ARM assembly.

By the end of Part I, you will have a working compiler that can
compile simple functions like this one:

<!--table>
<tr>
<td>
```js
function gcd(a, b) {
  while (a != b) {
    if (a > b) {
      a = a - b;
    } else {
      b = b - a;
    }
  }
  return a;
}                              &#8202;
```
</td>
<td>
</td>
</tr>
</table-->
```js
function factorial(n) {
  if (n == 0) {
    return 1;
  } else {
    return n * factorial(n - 1);
  }
}
```

Into ARM assembly code like this:

```arm
.global factorial
factorial:
  push {fp, lr}
  mov fp, sp
  push {r0, r1}
  ldr r0, =0
  push {r0, ip}
  ldr r0, [fp, #-8]
  pop {r1, ip}
  cmp r0, r1
  moveq r0, #1
  movne r0, #0
  cmp r0, #0
  beq .L1
  ldr r0, =1
  b .L2
.L1:
  ldr r0, =1
  mov r1, r0
  ldr r0, [fp, #-8]
  sub r0, r0, r1
  bl factorial
  mov r1, r0
  ldr r0, [fp, #-8]
  mul r0, r0, r1
.L2:
  mov sp, fp
  pop {fp, pc}
```


Part II talks about *more advanced* topics in *less details*.
It explores several different (often mutually exclusive)
directions in which you can take your compiler.

## Draft Table of Content

Introduction

Part I

* Compiler structure overview
* Representing programs using AST
* Lexing and parsing
* Introduction to ARM assembly
* Emitting assembly from an AST

Part II

* Static type checking
* Dynamic typing
* More primitive types: null, bool, char
* Foreign calls
* System calls
* Heap allocation: arrays, strings, records
* Garbage collector

Appendix: Running ARM code

* Linux
  * Running ARM code natively on Raspberry Pi
  * Running ARM code natively on a cloud VM instance
  * Emulating ARM with QEMU on Linux
  * Emulating ARM with Android NDK
* Windows
  * Emulating ARM with QEMU on Windows
  * Emulating ARM with QEMU on WSL
  * Emulating ARM with QEMU on Cygwin
  * Emulating ARM with Android NDK
  * Visual Studio workflow
* macOS
  * Emulating ARM with QEMU on macOS


<center><img src=./keleshev.jpg width=200 height=200 style=float:right /></center>
## About the author

My name is Vladimir Keleshev,
I have worked with compilers both commercially
and in open-source.
My fondness of ARM assembly stems from
my previous work in embedded systems.
Currently, I work in finance
with domain-specific languages.
I'm [@keleshev](https://twitter.com/keleshev) on Twitter.

<br />
<script async data-uid="7ee5be9f4e" src="https://motivated-writer-7421.ck.page/7ee5be9f4e/index.js"></script>

<!--
## It's coming summer 2020

When I write blog posts I usually spent the first half
of the time writing the code and develoing the idea, and
the second half on the prose.
This book will be no exception.

At the moment I have finished writing
the code, and I am very happy with the results.
I expect the book to be ready early summer 2020, and a draft to
be available even sooner.

-->



<!--script async data-uid="129429cd71" src="https://motivated-writer-7421.ck.page/129429cd71/index.js"></script-->



<center><img src=./dragon.jpg /></center>

<center><em>Illustration by [@PbKatiuska](https://twitter.com/PbKatiuska)</em></center>
