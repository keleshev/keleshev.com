---
title: "Appendix B: GAS v. ARMASM Syntax • Compiling to Assembly from Scratch"
---

```{=html}
<header>
<h1><small><small>Appendix B</small></small><br/>GAS <em>v.</em> ARMASM Syntax</h1>
<a href='./#table-of-contents'>Compiling to Assembly from Scratch</a>
<br/>by <a href='/'>Vladimir Keleshev</a>
</header>
```


\chapter{GAS \textit{v.} ARMASM Syntax}

Two different syntaxes are used for ARM assembly.
The first one is the GNU Assembler (GAS) syntax.
It is also supported by the official ARM toolchain based on Clang called `armclang`.

The other one is the legacy ARMASM syntax.
Most likely, you will not need to deal with it, but I include a small Rosetta Stone–style (side-by-side) comparison cheat sheet for completeness.

\newpage

## GNU Assembler Syntax

```js
/* Hello-world program.
   Prints "Hello, assembly!" and exits with code 42. */

.data
  hello:
    .string "Hello, assembly!"

.text
  .global main
  main:
    push {ip, lr}

    ldr r0, =hello
    bl printf

    mov r0, #41
    add r0, r0, #1  // Increment 41 by one.

    pop {ip, lr}
    bx lr
```


\newpage

## Legacy ARMASM Syntax

```
; Hello-world program.
; Prints "Hello, assembly!" and exits with code 42.

  AREA ||.data||, DATA
hello
  DCB  "Hello, assembly!",0

  AREA ||.text||, CODE
main PROC
  push {ip, lr}

  ldr r0, =hello
  bl printf

  mov r0, #41
  add r0, r0, #1  ; Increment 41 by one.

  pop {ip, lr}
  bx lr
```

\newpage

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}

\begin{center}
    \vfill
        \textit{This space is reserved for jelly stains}
    \vfill
\end{center}

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}

\newpage

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}

\newpage

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}

\endappendices


