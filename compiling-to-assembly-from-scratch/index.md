---
title: Compiling to Assembly from Scratch
twitter-card: true
twitter-title: Compiling to Assembly from Scratch
twitter-description: Anniversary sale — 40% off
twitter-image: "https://keleshev.com/compiling-to-assembly-from-scratch/anniversary-sale-card.png"
---


<h1>Compiling to Assembly<br/><small><small>from Scratch </small></small> </h1>

<center><img id=cover style="box-shadow: 0px 0px 46px -23px;" src=/compiling-to-assembly-from-scratch.jpg width=200 height=300 /></center>



<center><p> <a class=btn href=https://transactions.sendowl.com/packages/793969/FCCFED46/purchase rel=nofollow> Buy ebook • <strike>$45</strike> <b>$27</b> </a></p></center>



<!--<center><em>TypeScript — ARM — Lots of fun!</em></center> -->



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

This ebook will show you in detail
how you can build a compiler from scratch
that goes all the way from *source* to *assembly*.

The example code is written in a subset of **TypeScript** that reads like pseudocode.
The book describes the design and implementation of a compiler that emits
32-bit **ARM** assembly instructions.
All you need to know is how to program, the book will teach you enough compiler theory and assembly programming to get going.

<script src=https://transactions.sendowl.com/assets/sendowl.js></script>

> <h2 class=h2-card >Buy now and get the following:</h2>
>
> <div style=float:right;margin-left:20px> <center> <!--a class=btn-dis><b>$45</b></a--><br/> <img style="box-shadow: 0px 0px 46px -23px;" src=/compiling-to-assembly-from-scratch.jpg width=200 height=300 /><!--p><a class=btn-dis> Buy •  <b>$45</b> </a></p-->   <p><a class=btn href=https://transactions.sendowl.com/packages/793969/FCCFED46/purchase rel=nofollow> Buy ebook • <strike>$45</strike> <b>$27</b> </a> <br/> <small><small><em>Excl. <span >EU VAT</span></em></small></small> </p> </center></p> </div>
>
>  <br/>
>
>  * Complete book
>
>  * All future revisions
>
>  * Formats: PDF, EPUB, MOBI
>
>  * DRM-free
>
>  * Source code *(link in the book)*
>
>  * Access to the book's Discourse forum <br/> *(invite in the book)*<br/>
>
>  <br/>
>  <br/>
>  <br/>
>




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

If this book targeted Intel x86-64 instead of ARM, it would have been two times as long
and&hairsp;—&hairsp;more likely&hairsp;—&hairsp;never written.
Also, with 160 *billion* devices shipped, we better get used to the fact
that ARM is the dominant instruction set architecture today.

In other words… ARM is a good start.
After learning it, you will be better equipped
for moving to x86-64 or the new ARM64.

*Will you be able to run the code your compiler produces?*

I bet you will! The Appendix contains numerous ways
to execute ARM code, starting from Raspberry Pi,
cloud VM, to emulating ARM on Linux and Windows.

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

## Book Contents


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

This code won't win any awards, and an optimizing compiler
could do much better, but it's a start!

Part II talks about *more advanced* topics in *less details*.
It explores several different (often mutually exclusive)
directions in which you can take your compiler.

* * *

<style>#excerpt:hover { border-bottom: 0 !important; }</style>
<center><a id=excerpt href=./excerpt-compiling-to-assembly-from-scratch.pdf><img style="box-shadow: black 0px 0px 46px -23px;"  src=./book-preview.png width=400 height=300 /></a></center>

<br/>
<center><a class=btn href=./excerpt-compiling-to-assembly-from-scratch.pdf> Read excerpt </a></center>

## Print edition?

At the moment, I'm working on bringing the print edition of the book to reality.
However, there's no timeline for it yet.
You know, print is a bit harder than digital.
I need to be 100% confident about each word in the book before it is sent to the press.
However, I know that nobody likes buying the same book twice.
So, if you buy the ebook today, I make a promise to give you a discount, once the print edition is out.

## Can't afford it?

If due to circumstances you can't afford to buy the book—write me an email at [vladimir@keleshev.com](mailto:vladimir@keleshev.com), and I'm sure we can figure something out!

<center><img src=/keleshev.jpg width=200 height=200 style=float:right /></center>

## About me

My name is Vladimir Keleshev,
I have worked with compilers both commercially
and in open-source.
My fondness of ARM assembly stems from
my previous work in embedded systems.
Currently, I work in finance
with domain-specific languages.

## Questions?

Contact me at [vladimir@keleshev.com](mailto:vladimir@keleshev.com)
or on Twitter at
<a href="https://twitter.com/keleshev">@keleshev</a>.

<br />

<!--
> <h2 class=h2-card >Be the first to know when the book is finalized!</h2>

> <center>Reading a draft is not your style? I get it. Subscribe to be notified when the book is finalized (and related news about the book and compilers).</center>
>
>
> <center><a href=https://sellfy.com/p/bkz0pv/ id=bkz0pv class=sellfy-buy-button data-text=Pre-order></a></center>
>
> <script async data-uid="f6381e8cdd" src="https://motivated-writer-7421.ck.page/f6381e8cdd/index.js"></script>
>
> <center><small>You can unsubscribe at any time</small></center>

-->

<!--script async data-uid="129429cd71" src="https://motivated-writer-7421.ck.page/129429cd71/index.js"></script-->



<center><img src=/dragon.png width=256 height=260 /></center>
<br/>
<center><em>Illustrations by <a href="https://twitter.com/PbKatiuska">@PbKatiuska</a></em></center>
