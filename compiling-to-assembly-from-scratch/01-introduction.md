---
title: "1. Introduction • Compiling to Assembly from Scratch"
---

```{=html}
<header>
<h1><small><small>Chapter 1</small></small><br/>Introduction</h1>
<a href='./#table-of-contents'>Compiling to Assembly from Scratch</a>
<br/>by <a href='/'>Vladimir Keleshev</a>
</header>
```


<!-- TODO: move this, this is common to all pages -->
\titleformat{\chapter}[display]{\bfseries\centering}{\huge Chapter \thechapter}{1em}{\Huge #1}

\chapter{Introduction}
\includegraphics{chapter-illustrations/1.png}
\newpage

\setlength{\epigraphwidth}{0.5\textwidth}
\epigraph{It is not the gods who make our pots}{\textit{Ancient proverb}}

```{=html}
<p style="text-align: right">It is not the gods who make our pots<br/><em>Ancient proverb</em><p>
```

Welcome to the wonderful journey of writing your own compiler!

Picking up this book, you are probably already quite convinced that you want to understand how compilers work, and maybe even want to write one.
Nevertheless, here's a list of some of the reasons to do it:

 * Writing a compiler is the ultimate step in understanding how computers work and how they execute our programs.
 * By writing a small compiler, you can see that they are programs, just like others, and they are not magic made by gods.
 * By understanding assembly and how compilers translate your programs to it, you can better grasp the performance of the programs you write.
 * It will allow you to see the trade-offs of different language features more clearly, so you are better informed when to use them and how to use them effectively.
 * Learning about parsing will help you deal with unstructured data, like scraping, or dealing with a data format for which you don't have a library.
 * It will also prepare you for making your own domain-specific languages, when necessary, for the tasks at hand.
 * It may be a first step into the field of compiler engineering, a lucrative and exciting job.
 * And finally, it will allow you to experience the fun and excitement of creating and experimenting with a language of your own making!

The topic of compiler construction is the single most researched topic in computer science.
Nothing else comes close.
So there's a massive amount of useful techniques and algorithms in compiler literature.
And it turns out, a lot of it is very applicable to our day-to-day programming.
There's also a school of thought that, in the end, maybe all programs are compilers.
Maybe we are not writing web apps, for example, but compilers from DOM nodes to JSON and from JSON to SQL, who knows!

<!--, it's just that whatever we are working on today is not as well researched, at the moment.-->

\newpage


## Structure of the book

The book describes the design and implementation of a compiler written in TypeScript, which compiles a small language to 32-bit ARM assembly.

The book consists of two parts.

*Part I* describes the design and development of a minimal *baseline compiler* in great detail.
We call it a *baseline compiler* because it lays the foundation for developing more advanced features introduced in *Part II*.
The *implementation language* of the compiler is TypeScript.
But the compiler's *source* or *input* language is a *subset* (or a simplified version) of TypeScript.
This subset consists of things common to any practical programming language, not specific to TypeScript: arithmetic and comparison operators, integer numbers, functions, conditional statements and loops, local variables, and assignments.
We call this language the *baseline language*.
It can express simple programs and functions, like this one, for example:

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

*Part II* builds upon the *baseline compiler* and describes various *compiler extensions* in lesser detail.
Those extensions are often mutually exclusive (like static typing and dynamic typing), but they all use the baseline compiler as the foundation.

*Appendix A* describes how to run the ARM assembly code the compiler produces.
You can skip this if you're developing your compiler on a computer which is based on an ARM processor with a 32-bit operating system like Raspberry Pi OS (formerly Raspbian).
However, if you are running an x86-64 system like those from Intel and AMD, you need to see *Appendix A*.

*Appendix B* describes the differences between the two mainstream ARM assembly syntaxes: the GNU assembler (GAS) syntax, and the legacy ARMASM syntax.

## Why ARM?

In many ways, the ARM instruction set is what makes this book possible.

Compared to Intel x86-64, the ARM instruction set is a work of art.

Intel x86-64 is the result of evolution from an 8-bit processor, to a 16-bit one, then to a 32-bit one, and finally to a 64-bit one.
At each step of the evolution, it accumulated complexity and cruft.
At each step, it tried to satisfy conflicting requirements.

 * Intel x86-64 is based on *Complex Instruction Set Architecture* (CISC), which was initially optimized for writing assembly by hand.
 * ARM, on the other hand, is based on *Reduced Instruction Set Architecture* (RISC), which is optimized for writing compilers.

*Guess which one is an easier target for a compiler?*

If this book targeted x86-64 instead of ARM, it would have been two times as long and—more likely—never written.
Also, with *hundreds* of *billions* devices shipped, we better get used to the fact that ARM is the dominant instruction set architecture today.

In other words, ARM is a good start. After learning it, you will be better equipped for moving to x86-64 or the newer ARM64.

## Why TypeScript?

This book describes the design and development of a compiler written in TypeScript, which compiles a small language that also uses TypeScript syntax.

The compiler doesn't have to be written in TypeScript.
It could be written in any language, but I had to pick.
I have used a straightforward subset of TypeScript for the examples, to make it readable for anyone who knows one or more mainstream languages.

The next chapter, *TypeScript Basics*, gives you a quick overview of the language.

## How to read this book

*Part I* is structured linearly, with each chapter building upon the previous one.
However, don't feel guilty skipping chapters if you are already familiar with a topic.

If you plan to follow along and implement the compiler described in this book (or a similar one), I recommend first to read *Part I* without writing any code.
Then you can go back to the beginning and start implementing the compiler while skimming *Part I* again.

The book uses the *parser combinators* approach to create the parser; however, if you know a different technique, feel free to use it instead.

The book is also sprinkled with the tree types of notes.

> **Note**
>
> These are general notes.

* * *

> **Explore**
>
> The **Explore** notes contain suggestions and ways to try out things on your own.
> You might find them useful for practicing and building your confidence, or you might find it more fitting to have a minimal working compiler first, and only then optionally come back to these.

* * *

> **Well, actually…**
>
> These contain some pedantic notes which are beside the point, but the book would be incomplete without them.

We will also use *code folding* in the code snippets.
We will use ellipsis (`…`) to denote that some code in a snippet was omitted, usually because it was already shown before.

```js
function factorial(n) {
  var result = 1;
  while (n != 1) {…}  // Here
  return result;
}
```

*Part II* is structured in mostly independent sections.
Feel free to reach just for the parts you are interested in.
No need to read both about *static typing* and *dynamic typing* if you want to focus only on one of these topics.

```{=html}
<center><a href="./02-typescript-basics">Next: Chapter 2. TypeScript Basics</a></center>
```
