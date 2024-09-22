---
title: "9. Introduction to Part II • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 9</small></small><br/>Introduction to Part II<br/><br/></h1>
```

\part{Compiler Extensions} 
\newpage
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}  

\chapter{Introduction to Part II}
\includegraphics{chapter-illustrations/9.png}
\newpage

Before extending the compiler, let's discuss the language we have implemented so far.

Is our language memory-safe?
What is memory safety, anyway?
Simply speaking, a language is memory-safe if it does not allow you to write a program that causes a segmentation fault.
The baseline language is memory-safe if we limit ourselves to calling functions that we have defined ourselves.
However, our calling convention allows us to call arbitrary `libc` functions.
You can find creative ways to call these functions that will lead to a segmentation fault (try `free(42)`).
So, unless we do something about that, the baseline language is not memory-safe.

A way to fix that is to introduce a prefix for function labels.
For example, a function `factorial` can be compiled with a label `ts$factorial:`, and a call to `factorial` can be compiled to a jump to `ts$factorial`.
This way, you can only call functions that are defined in the source language, or that had explicit wrappers written in assembly.
These wrappers can be auto-generated by the compiler and also handle type conversion, if necessary.

Is our language dynamically-typed?
Or is it statically-typed?
Both and neither!
The baseline language supports only integer numbers.
So, it could be thought of as a dynamically-typed language with only one data type, or as a statically-typed language with one static type.
But we are soon to change this.

However, before we explore static and dynamic typing, we need to have more than one data type in our language.
We will start by introducing booleans, undefined, and then arrays.
First, we will introduce them in an unsafe/untyped manner, and then we will apply static/dynamic treatment to them.

```{=html}
<center><a href="./10-primitive-scalar-data-types#fold">Next: Chapter 10. Primitive Scalar Data Types</a></center>
```