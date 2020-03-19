---
title: EAX x86 Register: Meaning and History
---




EAX x86 Register: Meaning and History
=====================================

<center>2020-04-18</center>

Usually x86 tutorials
don't spend much time explaining
the historical perspective of things,
or the naming of things.
When learning x86 assembly, you're usually told:
*Here's EAX. It's a register. Use it.*

<big>So, what do exactly those letters stand for? E–A–X.      </big>

I'm afraid there's no short answer!

## The 8008

In 1972, after an odd sequence of events,
Intel introduced the world's first 8-bit microprocessor,
the *8008*.
Back then Intel was primarily a vendor of memory chips.
The 8008 chip was commissoned by Computer Terminal Corporation (CTC)
for their new Datapoint 2200 programmable terminal.
But the chip was delayed and did not meet CTC expectations.
So Intel added a few general-purpose instructions to it
and marketed the chip to other customers.

8080 had *seven* 8-bit registers:

```ocaml
A
B
C
D
E
H
L
```

The `A` stood for *accumulator* which was an implicit
operand and return value of arithmetic and logical operations.

You might think—*gee, seven is a very odd number or tegisters*—and
would be right!
The registers were encoded as three bits of the instruction,
so it allowed 8 combinations.
The last one was for pseudo-register called `M`.
It stood for *memory*.
When an instruction referenced the `M` register,
instead of operating on a register it operated
on a single byte of memory that was referenced
by the 16 bit stored in registers registers `H` and `L`.
They were referring to the *high* and the *low* byte of the address.
That was the only available way to reference memory on 8008.

So, `A` was an accumulator, `H` and `L` were used for
addressing memory, however, `B`, `C`, `D`, `E` were
completely generic and interchangable.

## The 8086

In 1979, Intel is already a microprocessor company,
and their flagship processor iAPX 432 is delayed.
So as a stop-gap measure they introduce the 8086,
a 16 bit microprocessor
derived from 8080 which was itself is derived from 8008.

To leverage its existing customer base, Intel made 8086
software-compatible down to 8008.
A translator program would translate
from 8008 assembly to 8086 assembly.
For that to work well, 8086 instruction set architecture
had to be a superset of 8008, inheriting the design decisions.

The new registers had to map well to the 8008 registers,
so the following scheme was introduced:

```ocaml
AH AL | AX
BH BL | BX  base
CH CL | CX  count
DH DL | DX  data
```

There were four main 16 bit registers,
and each of them had their
high and low bytes mapped to 8-bit registers,
totalling at *eigth* eight bit registers.
This way, the seven 8008 registers could be
easily mapped to eight 8086 registers with one to spare.
The `M` pseudo-register was not needed any more,
since 8086 allowed for many memory addressing modes.

In the following figure you can see how exactly
the 8008 registers mapped to 8086 ones:

```ocaml
  A
H L
B C
D E

AH AL | AX
BH BL | BX  base
CH CL | CX  count
DH DL | DX  data
```

As you can see, the "free slot" left by the absence
of need for encoding the `M` register was used
to extend the accumulator.

At this point, none of the main registers were
truly generic.
Each had some instructions introduced that worked for
one of the registers, but didn't work for others.
So the mnemonic goes as: `BX` is base register,
`CX` is count register, `DX` is data register,
and `AX` is still the accumulator.

8086 also introduced pointer and index registers,
`SP`, `BP`, `SI`, `DI`,
as well as memory segments and segment registers,
`CS`, `DS`, `SS`, `ES`.

Segmented architecture deserves a story on its own,
as it is the result of maintaining backwards-compatibility
with 8080.

It's 1979, and by all accounts 8086 instruction set
architecture is already a mess.

<em>
To sum up, `AX` is the 16 bit accumulator,
which lower byte can be accessed as `AL`, and higher byte—as `AH`.
</em>

## x86

In 1985 Intel introduced 80386, the first 32-bit processor
in the x86 line.
An early batch of processors had a defect
in some 32 bit operatrions.
They were marked as *16-BIT S/W ONLY* and sold anyway.

Many new features were introduced, but 80386
continued to be *(mostly)* binary-compatible down to 8086.

The main registers were *e*xtended to 32 bits by
adding an E prefix:

```ocaml

|<-------- ---------EAX--------- -------->|
                     |<--------AX-------->|
                     |<---AH--->|---AL--->|

```

`AX` now referres to the lower half of `EAX`,
while `AH` and `AL` continued to refer to the `AX` halfs.

And that's how EAX got it's name.
*But wait, there's more to the story!*


## x86-64

In 2003 AMD takes the lead by introducing
the first 64-bit processor in the x86 lineage.
In *legacy mode* it is backwards-compatible down to 8086.

<svg xmlns="http://www.w3.org/2000/svg" style="background-color: rgb(255, 255, 255);" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="658px" height="131px" viewBox="-0.5 -0.5 658 131" content="<mxfile host=&quot;app.diagrams.net&quot; modified=&quot;2020-03-19T21:03:36.066Z&quot; agent=&quot;Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:73.0) Gecko/20100101 Firefox/73.0&quot; etag=&quot;f6KRbXQV17QPz3HW6jH4&quot; version=&quot;12.8.8&quot;><diagram id=&quot;ChDNRUbI87a4qMMUupB1&quot; name=&quot;Page-1&quot;>7ZnZctowFIafhsswtrwAl2xJZtpOO6WT5VLYCnZrLFcWW5++Epa8yQQK2LQULhLpSD6yzv9pdcsYztcPBEbeJ+yioAU0d90yRi0AurrB/nLDJjGYtpkYZsR3E5OeGSb+LySMmrAufBfFhYoU44D6UdHo4DBEDi3YICF4Vaz2hoNiqxGcIcUwcWCgWp99l3qiW5aW2R+RP/Nky7omSuZQVhaG2IMuXuVMxrhlDAnGNEnN10MU8NjJuCTP3e8oTV+MoJAe8oB5//T68Fn//vTD/PA8+LbGxAR3wssSBgvR4RawA+Zv4PpL/tJ0IyJh/1zwNx284ZDexVud+qyCDiIm9SArZ6kZ//+1/8KScB6xdDiNo6TownlN9m5KTuqcdMOivY2TtIKCV0DwInQRj7/OileeT9Ekgg4vXbHRwmwenQeimLct+NdB6m2JCEXrnZLrKUhsACI8R5RsWBX5gGRPDD5givwqQ9mWNi+HsbRBMXpmqesMMJYQjP0Bb6Be3thLaXyC0aY+PVAjFLp9Pk+wnBPAOPYdViumkFDVvFct5CqzyV6tclpYFVJIG0EBpP6y6L5KH9HCF+yzhneioNsliWO8IA4ST+WnkZKjjr3HEQvdDFHF0RaXtNvHE2TURtBYEmSAG0Gq8KZZEr57LoLKjmomyKyNIAmQbt8AUnW3tdJqpJ0JIMVRzQBZ9QH0MQGoe+Ongp9uSXZwLn7Kjmrmxz4LPyo8jzd4Dp98joVnL4U1w9OpgGe3pCEO0b8tnHKGOXbjquyArWaF69a2aoxvR+2LH7XLu+Oqo7YBKoZJbUftXn27lAZw+8/wUZanCnzSk3Yj+MgL2Bw/fHf6t8WtvBpXxK3baNiqblSveX1WNtNnu1hqeH3WwYnKMT3I5oVlNJl55Zm2JbOjdb5wtBG5YxUHWhKRfXuOi10YGb22bfWyX6eob+dIULhfwyhC1zQrVbeQ1zzKmYztXv5XlLJ37GGqvOw1fJmsV90FXrOOduc9HdOvricfis+mI8tmn0iT6tl3ZmP8Gw==</diagram></mxfile>"><defs></defs><g><rect x="8" y="90" width="640" height="40" rx="6" ry="6" fill="#ffffff" stroke="#000000" pointer-events="all"></rect><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 638px; height: 1px; padding-top: 110px; margin-left: 9px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; "><div style="font-size: 12px">RAX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <br style="font-size: 12px"></div></div></div></div></foreignObject><text x="328" y="114" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">RAX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</text></switch></g><path d="M 14.37 10 L 641.63 10" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 9.12 10 L 16.12 6.5 L 14.37 10 L 16.12 13.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><path d="M 646.88 10 L 639.88 13.5 L 641.63 10 L 639.88 6.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 1px; height: 1px; padding-top: 10px; margin-left: 328px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; background-color: #ffffff; white-space: nowrap; "><div style="font-size: 12px">RAX, 64 bit</div></div></div></div></foreignObject><text x="328" y="14" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">RAX, 64 b...</text></switch></g><path d="M 334.37 30 L 641.63 30" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 329.12 30 L 336.12 26.5 L 334.37 30 L 336.12 33.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><path d="M 646.88 30 L 639.88 33.5 L 641.63 30 L 639.88 26.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 1px; height: 1px; padding-top: 30px; margin-left: 488px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; background-color: #ffffff; white-space: nowrap; "><div style="font-size: 12px">EAX, 32 bit</div></div></div></div></foreignObject><text x="488" y="34" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">EAX, 32 b...</text></switch></g><path d="M 494.37 50 L 641.63 50" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 489.12 50 L 496.12 46.5 L 494.37 50 L 496.12 53.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><path d="M 646.88 50 L 639.88 53.5 L 641.63 50 L 639.88 46.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 1px; height: 1px; padding-top: 50px; margin-left: 568px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; background-color: #ffffff; white-space: nowrap; "><div style="font-size: 12px">AX, 16 bit</div></div></div></div></foreignObject><text x="568" y="54" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">AX, 16 bit</text></switch></g><path d="M 574.37 70 L 641.63 70" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 569.12 70 L 576.12 66.5 L 574.37 70 L 576.12 73.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><path d="M 646.88 70 L 639.88 73.5 L 641.63 70 L 639.88 66.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 1px; height: 1px; padding-top: 70px; margin-left: 608px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; background-color: #ffffff; white-space: nowrap; "><div style="font-size: 12px">AL, 8 bit</div></div></div></div></foreignObject><text x="608" y="74" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">AL, 8 bit</text></switch></g><path d="M 494.37 70 L 561.63 70" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 489.12 70 L 496.12 66.5 L 494.37 70 L 496.12 73.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><path d="M 566.88 70 L 559.88 73.5 L 561.63 70 L 559.88 66.5 Z" fill="#000000" stroke="#000000" stroke-miterlimit="10" pointer-events="all"></path><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 1px; height: 1px; padding-top: 70px; margin-left: 528px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; background-color: #ffffff; white-space: nowrap; "><div style="font-size: 12px">AH, 8 bit</div></div></div></div></foreignObject><text x="528" y="74" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">AH, 8 bit</text></switch></g><path d="M 8 110 L 8 0" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><rect x="328" y="90" width="320" height="40" rx="6" ry="6" fill="#ffffff" stroke="#000000" pointer-events="all"></rect><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 318px; height: 1px; padding-top: 110px; margin-left: 329px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; "><div style="font-size: 12px">EAX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <br style="font-size: 12px"></div></div></div></div></foreignObject><text x="488" y="114" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">EAX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</text></switch></g><rect x="488" y="90" width="160" height="40" rx="6" ry="6" fill="#ffffff" stroke="#000000" pointer-events="all"></rect><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 158px; height: 1px; padding-top: 110px; margin-left: 489px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; "><div style="font-size: 12px">AX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <br style="font-size: 12px"></div></div></div></div></foreignObject><text x="568" y="114" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">AX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</text></switch></g><rect x="568" y="90" width="80" height="40" rx="6" ry="6" fill="#ffffff" stroke="#000000" pointer-events="all"></rect><g transform="translate(-0.5 -0.5)"><switch><foreignObject style="overflow: visible; text-align: left;" pointer-events="none" width="100%" height="100%" requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"><div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; align-items: unsafe center; justify-content: unsafe center; width: 78px; height: 1px; padding-top: 110px; margin-left: 569px;"><div style="box-sizing: border-box; font-size: 0; text-align: center; "><div style="display: inline-block; font-size: 12px; font-family: Helvetica; color: #000000; line-height: 1.2; pointer-events: all; white-space: normal; word-wrap: normal; ">AL</div></div></div></foreignObject><text x="608" y="114" fill="#000000" font-family="Helvetica" font-size="12px" text-anchor="middle">AL</text></switch></g><path d="M 648 110 L 648 0" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 327.66 20 L 328 110" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 488 40 L 488 110" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path><path d="M 568 60 L 568 110" fill="none" stroke="#000000" stroke-miterlimit="10" pointer-events="stroke"></path></g><switch><g requiredFeatures="http://www.w3.org/TR/SVG11/feature#Extensibility"></g><a transform="translate(0,-5)" xlink:href="https://desk.draw.io/support/solutions/articles/16000042487" target="_blank"><text text-anchor="middle" font-size="10px" x="50%" y="100%">Viewer does not support full SVG 1.1</text></a></switch></svg>


