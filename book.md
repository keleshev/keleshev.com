Compiling to Assembly<br/><small>from Scratch<br/><small><em></em></small></small>
==================================

<center>— the book —<br/>

<em>ETA: Summer 2020</em></center>


<!--p></p>
<center>⁂</center>
<div style="
 border black; background: ; margin: 0 8.5em; border: 1px solid black; height: 27em; box-shadow: 1px 1px 20px 2px #888888;
//background-image: linear-gradient(to bottom, rgba(255,255,255,1.0), rgba(255,255,255,0.0)), url('./mill2.jpg');
">
<!--img src='./mill.png' width=414 height=414/-->
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<h1 style='line-height:0.8em'><small><center><small></small><br>Compiling to Assembly<br><small>from Scratch</small></center></small></h1>
<br/>
<br/>
<br/>
<br/>

<center>Vladimir Keleshev</center>

</div>
<p>
<br/>
</p-->


*So, you've been trying to learn how programming languages
and compilers work?*
Perhaps, you've learned about compiling to JavaScript,
or about building an interpreter. Or, maybe, about
compiling to bytecode? All good steps.

*But there's a tension building up.*

Because it feels a bit like cheating.
Because you know that somewhere, somehow the code you write
is translated to assembly instructions. To the machine language.
That's where the rubber hits the road. That's where it gets hot.
And, oh-so-many resources are hesitant to cover this part.
But not this book.

This *small* book will show using detailed example code
written in
that goes all the way from source to assembly.

The example code is wirtten in **TypeScript**, a dialect of **JavaScript**.
The compiler generates 32-bit **ARM** assembly instructions.

## Why ARM?

In many ways the ARM instruction set is what makes this book possible.

Compared to Intel x86-64, the ARM instruction set is a work of art.

Intel x86-64 is the result of evolution from an 8-bit processor,
to a 16-bit one, then to a 32-bit one, and finally to a 64-bit one.
At each step of the evolution it accumulated complexity and cruft.
At each step it tried to satisfy confilicting requirements.

* Intel x86-64 is based on *Complex Instruction Set Atchitecture* (CISC),
which was initially optimized for writing assembly by hand.
* ARM, on the other hand, is based on *Reduced Instruction Set Architecture* (RISC),
which is optimized for writing compilers.

*Guess, which one is an easier target when writing compilers?*

If this book targeted Intel x86-64 instead of ARM it would have been three times as long,
and&hairsp;—&hairsp;more likely&hairsp;—&hairsp;never written.
Also, with 160 *billion* devices shipped, we better get used to the fact
that ARM is the dominant instruction set architecture today.

Or, in other words, ARM is a good start.
After learning it you will be better equipped
for moving to x86-64 or the new ARM64.

*Will you be able to execute the code your compiler produces?*

I bet you will! The Appendix will contain a bazillion ways
to run execute ARM code, starting from Raspbery Pi,
could VM, to various ways to emulate ARM on Linux,  Windows, and macOS.

## Why TypeScript?

First of all, you will be able to follow this book in any reasonable programming language.
For me, it was very hard to pick one for this job, and I'm very happy I've picked TypeScript.

TypeScript is probably nobody's favorite, but it's a good compromise:

* If you're comming from JavaScript background, then if you close your eyes at the
  type annotations, then TypeScript is just modern-day JavaScript.
* If you're comming from Java or C#, then you may know that TypeScript
  is brought to you by the same people who brought you C# (and Turbo Pascal),
  so you will feel right at home.

Don't worry if you've never seen TypeScript code before.
If you can read the following, you will most likely be able to just pick it up,
as the book goes:

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
language features in the code, and I will try to provide
extensive commentary regarding how any tricky parts
could be implemented in other languages or paradigms.

If you're into statically-typed functional programming
languages, like Haskell, OCaml, or Reason ML,
you will find that the provided class
structure has a direct translation to an algebraic data type.


<style>
  pre {
    border-left: 0;
    font-size: 16px;
    line-height: 1.5em;
  }

</style>

## Book Structure


The book consists of two parts. Part I
presents a *detailed*, *step-by-step* guide on how
to develop a small "baseline" compiler that can compile simple
programs to ARM assembly.

By the end of Part I you will have a working compiler that can
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
It explores several different (often mutually exclussive)
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


## It's comming summer 2020

When I write blog posts I usually spent the first half
of the time writing the code and develoing the idea, and
the second half on the prose.
This book will be no exception.

At the moment I have finished writing
the code, and I am very happy with the results.
I expect the book to be ready early summer 2020, and a draft to
be available even sooner.










## In short

* DRM-free PDF,
  <small>more formats on request</small>
* Unlimited updates
* No libraries: everything is build from scratch
* No libraries: you'll see how to implement everything from scratch.
