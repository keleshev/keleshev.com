---
title: EAX x86 Register: Meaning and History
---


<span id=home><a title=Home href=/>☰</a></span>


EAX x86 Register: Meaning and History
=====================================

<center>2020-04-20</center>

Usually, x86 tutorials
don't spend much time explaining
the historical perspective of design and naming decisions.
When learning x86 assembly,
you're usually told something along the lines:
*Here's `EAX`. It's a register. Use it.*

<big>So, what exactly do those letters stand for? E–A–X.      </big>

I'm afraid there's no short answer!
We'll have to go back to 1972…

## 8008

In 1972, after an odd sequence of events,
Intel introduced the world's first 8-bit microprocessor,
the *8008*.
Back then, Intel was primarily a vendor of memory chips.
The 8008 was commissioned by the Computer Terminal Corporation (CTC)
for their new Datapoint 2200 programmable terminal.
But the chip was delayed and did not meet CTC expectations.
So Intel added a few general-purpose instructions to it
and marketed the chip to other customers.

8080 had *seven* 8-bit registers:

<center><img src=8008.svg></center>

`A` stood for *accumulator*, which was an implicit
operand and return value of the arithmetic and logical operations.

You might think—*gee, seven is a very odd number of registers*—and
would be right!
The registers were encoded as three bits of the instruction,
so it allowed for eight combinations.
The last one was for a pseudo-register called `M`.
It stood for *memory*.
`M` stood for the memory location
pointed by the combined registers `H` and `L`.
They were referring to the *high* and the *low* byte of the address.
That was the only available way to reference memory in 8008.

So, `A` was an accumulator, `H` and `L` were also used for
addressing memory. However, `B`, `C`, `D`, `E` were
completely generic and interchangeable.

## 8086

In 1979, Intel was already a microprocessor company,
and their flagship processor iAPX 432 is delayed.
So as a stop-gap measure, they introduce 8086,
a 16-bit microprocessor
derived from 8080, which was itself derived from 8008.

To leverage its existing customer base, Intel made 8086
software-compatible down to 8008.
A simple translator program would translate
from 8008 assembly to 8086 assembly.
For that to work well, 8086 instruction set architecture
had to map well to 8008, inheriting many design decisions.

8086 had eight 16-bit registers and eight 8-bit registers,
and they overlapped as follows:

<center><img src=8086.svg></center>

8086 instructions had a bit flag that specified
whether the three-bit encoding of a register
referred to one of eight 8-bit registers,
or to one of eight 16-bit registers.

As you can see from the figure above,
data in the first four 16-bit registers could
also be accessed by one of the eight 8-bit registers.

> `AX` was an e*X*tended accumulator, while `AH` and `AL`
> could be thought of as 8-bit registers on their own
> or as a way to access the *H*ight and the *L*ow
> bytes of `AX`.

Since 8008 had seven 8-bit registers,
they could be mapped well to the eight 8086 registers,
with one to spare.

The `M` pseudo-register was not needed anymore
since 8086 allowed for many memory addressing modes.
Hence, it freed an encoding for an additional register.

In the following figure you can see how exactly
the 8008 registers were mapped to the 8086 ones:

<center><img src=8008vs8086.svg></center>


<!--center><img src=ax.svg></center-->

Even though many arithmetic and logical operations
could work on any of these registers,
none of the registers were truly generic at this point.
Each had some instructions introduced that worked for
one of the registers but didn't work for others.
The mnemonics are: `BX` is *base register*,
`CX` is *count register*, `DX` is *data register*,
and `AX` is still the *accumulator*.

The new
`SP` is *stack pointer*, `BP` is *base pointer*,
`SI` is *source index*, `DI` is *destination index*.
But we won't go into details about them here.

8086 also introduced the segment registers, but they
were very much a separate beast.
Segmented architecture deserves a story on its own,
as it is the result of maintaining backward-compatibility
with 8080.

*It's 1979, and by all accounts, 8086 instruction set
architecture is already a mess.*

<!--em>
To sum up, `AX` is the 16 bit accumulator,
which lower byte can be accessed as `AL`, and higher byte—as `AH`.
</em-->

## x86

In 1985 Intel introduced 80386, the first 32-bit processor
in the x86 line.
An early batch of processors had a defect
in one of the 32-bit operations.
They were marked as *16-BIT S/W ONLY* and sold anyway.

Many new features were introduced, but 80386
continued to be *(mostly)* binary-compatible down to 8086.

The main registers were *E*xtended to 32 bits by
adding an `E` prefix:

<center><img src=eax.svg></center>


> `EAX` is now the *E*xtended e*X*tended *A*ccumulator.
> `AX` now refers to the lower half of `EAX`,
> while `AH` and `AL` continue to refer to the two `AX` bytes.

And that's how `EAX` got its name.

*But wait, there's more to the story!*


## x86-64

In 2003 AMD effectively takes over the architectural leadership
and introduces
the first 64-bit processor in the x86 lineage.
In *legacy mode*, it is backward-compatible down to 8086.

The eight main registers are extended to 64 bits.

The extended registers get an `R` prefix that replaces
the `E` prefix. So the accumulator is now referred to as `RAX`:

<center><img src=rax.svg></center>

*Why `R`?*

Well, AMD wanted to streamline the register handling.
They introduced eight new registers called `R8` to `R15`.
They even discussed calling the extensions of the
existing eight registers as `R0` to `R7`.
But they recognized that many instructions
have mnemonics that refer to one of the register
letters like `A` or `B`.
So they kept the
original names, replacing `E` with `R`.
That also provided some consistency with the new `R8`–`R15`.

The new registers also got their "narrow" versions.
Take `R15`, for example:

<center><img src=r15.svg></center>

And that was a quick history of x86 accumulator!
From an 8-bit `A` of 8008, to 16-bit `AX` of 8086,
to 32-bit `EAX` of 80386, to 64-bit `RAX`.

## References

For the early history of 8008, 8080, and 8086, I recommend
[Stephen Morse's history piece][MORSE]. [&#9632;](/ "Home")

[MORSE]: https://stevemorse.org/8086history/8086history.pdf


<center>


<br/>
<br/>
⁂
<br/>
<br/>

<style>
#cover {
  border: 1px solid black;
  width: 500px;
  color: black;
  display: block;
}

</style>



<h2>Did you know, I’m writing a book about compilers?</h2>


<div id=cover >
<a id=cover href=/compiling-to-assembly-from-scratch-the-book >

<br/>

<h1>Compiling to Assembly<br/><small>from Scratch<br/><small><em></em></small></small></h1>

— the book —<br/>
<br/>
<br/>

<img src=/dragon.png width=150 height=188 />

<br/>
<br/>
<br/>


<em>ETA: Summer 2020</em>
<p>Vladimir Keleshev</p>
<br/>

</a>
</div>

</center>

<br/>
