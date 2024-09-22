---
no-fleuron: true
title: Compiling to Assembly from Scratch
twitter-card: false
twitter-title: Compiling to Assembly from Scratch
twitter-description: Black Friday — 40% off
twitter-image: "https://keleshev.com/compiling-to-assembly-from-scratch/black-friday-card.png"
---

<h1>Compiling to Assembly<br/><small><small>from Scratch </small></small> </h1>

<div style="
    position: absolute;
    width: 100%;
    height: 500px; /* Adjust height as needed */
    background-image: url('./compiling-to-assembly-from-scratch-photo.jpg');
    background-repeat: repeat;
    background-size: cover;
    background-position: center;
    /* 700px is body width, 750px min viewport, -25px left margin */
    margin-left: min(-25px, calc((100% - 700px) / 2 * -1));
"> </div>
<div style=" height: 500px;"> </div>


<p></p>

<div style="margin: 0px 0;">
<a class="big-round-btn" href="https://www.lulu.com/shop/vladimir-keleshev-and-katiuska-pino/compiling-to-assembly-from-scratch/hardcover/product-579gk7z.html" style="width:220px; margin-left:86px; padding: 5px 0 4px 0;">
  <center>
    <table style="border: none">
      <tr>
        <td>
        </td>
        <td rowspan="2"><center> &nbsp;&nbsp; <b>$49</b> </center></td>
      </tr>
      <tr>
        <td>
          <center>
            Buy hardcover<br/>
            <small> at <em><b>lulu.com</b></em> </small>
          </center>
        </td>
      </tr>
    </table>
  </center>
</a>
<a href="#table-of-contents" class="big-round-btn-inverted" style="width:220px; margin-left:86px; padding: 15.5px 0 16.5px 0;">
  <center>
    <table style="border: none">
      <tr>
        <td><center>Read online for <b>free<b></center></td>
      </tr>
      <tr>
      </tr>
    </table>
  </center></a></div>

<br/>

<big><em>Have you been trying to learn how **compilers** and **programming languages** work?</em></big>

<!--table style="width: 100%">
  <tr>
    <td style="width:50%">
      <center>
        <a class="big-round-btn" href="#" style="width:66%">
          <table>
            <tr>
              <td>
              </td>
              <td rowspan="2"><center> &nbsp;&nbsp; <b>$49</b> </center></td>
            </tr>
            <tr>
              <td>
                <center>
                  Buy hardcover<br/>
                  <small> at <em><b>lulu.com</b></em> </small>
                </center>
              </td>
            </tr>
          </table>
        <a>
      </center>
    </td>
    <td style="width:50%">
      <center>
        <a href="#Contents" class="big-round-btn-inverted" style="width:66%">
          <table>
            <tr>
              <td><center>Read online for <b>free<b></center></td>
            </tr>
            <tr>
            </tr>
          </table>
        </a>
      </center>
    </td>
  </tr>
</table-->



Then come along! Let's make a compiler that goes all the way from *source* to *assembly* from scratch—no shortcuts!

This book will teach you enough compiler theory and assembly programming to get going.
It uses a subset of **TypeScript** that reads like pseudocode and targets **ARM** 32-bit instruction set.

<span id="table-of-contents" style="position:absolute">&nbsp;</span>

<h2>Table of Contents</h2>

1. [Introduction](./01-introduction#fold)
2. [TypeScript Basics](./02-typescript-basics#fold)

*Part I: Baseline Compiler*

3. [High-level Compiler Overview](./03-high-level-compiler-overview#fold)
4. [Abstract Syntax Tree](./04-abstract-syntax-tree#fold)
5. [Parser Combinators](./05-parser-combinators#fold)
6. [First Pass: The Parser](./06-first-pass-the-parser#fold)
7. [ARM Assembly Programming](./07-arm-assembly-programming#fold)
8. [Second Pass: Code Generation](./08-second-pass-code-generation#fold)

*Part II: Compiler Extensions*

9. [Introduction to Part II](./09-introduction-to-part-2#fold)
10. [Primitive Scalar Data Types](./10-primitive-scalar-data-types#fold)
11. [Arrays and Heap Allocation](./11-arrays-and-heap-allocation#fold)
12. [Visitor Pattern](./12-visitor-pattern#fold)
13. [Static Type Checking and Inference](./13-static-type-checking-and-inference#fold)
14. [Dynamic Typing](./14-dynamic-typing#fold)
15. [Garbage Collection](./15-garbage-collection#fold)

*Appendices*

<ol type="A">
 <li>
   [Running ARM Programs](./appendix-a-running-arm-programs#fold)
 </li>
 <li>
   [GAS *v.* ARMASM Syntax](./appendix-b-gas-v-armasm-syntax#fold)
 </li>
</ol>

<center><img src=/keleshev.jpg width=200 height=200 style="float:right; border-radius:200px; margin-top:50px" /></center>
## Author

My name is Vladimir Keleshev.
I am a software developer living and working just outside of Copenhagen.
I have worked with embedded systems, safety-critical systems,
compilers, and now in finance with domain-specific languages.

## Illustrator

The cover is illustrated by [Katiuska Pino](https://katiuskapino.com/#links).
She also drew 15 chapter illustrations that are exclusive to the print edition of the book.

## Print edition

Print edition consists of 207 pages, size 6×9" (152×229 mm), in matte hard cover, available at [lulu.com](https://www.lulu.com/shop/vladimir-keleshev-and-katiuska-pino/compiling-to-assembly-from-scratch/hardcover/product-579gk7z.html). ISBN: 978-87-980078-0-7.

## Ebook edition

This book was originally published in 2020 as ebook.
The online edition replaces the ebook edition.

## Citation

<small>
```
@book{Keleshev:2024,
  author="Vladimir Keleshev",
  title="Compiling to Assembly from Scratch",
  publisher="keleshev.com",
  year=2024,
  isbn="978-87-980078-0-7",
  note="Originally published in 2020 as ebook",
}
```
</small>


## Source code

Source code from the book is available on [GitHub](https://github.com/keleshev/compiling-to-assembly-from-scratch).
[Python](https://github.com/keleshev/compiling-to-assembly-from-scratch/tree/main/contrib/python) and [OCaml](https://github.com/keleshev/compiling-to-assembly-from-scratch/tree/main/contrib/ocaml) ports of the compiler are available as well.


## Questions? Comments? Feedback?

 * Email me at [vladimir@keleshev.com](mailto:vladimir@keleshev.com),
 * DM me at <a href="https://twitter.com/keleshev">@keleshev</a>, or
 * Open an issue or a pull request on [GitHub](https://github.com/keleshev/keleshev.com).


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

<style>
#spike { opacity: 1}
#spike:hover { opacity: 1.0}
#spike-2 { opacity: 0.0}
#spike-2:hover { opacity: 0}
</style>
<center style="height:122px; overflow: hidden; position:relative;">
  <img id="spike" style="position:relative" src=./spike.png width=256 height=260 />
  <!--img id="spike-2" style="position:relative" src=./spike-2.png width=256 height=260 /-->
</center>


<!--
<footer style="height:122px; overflow:hidden; position:relative;">
<div style="position:absolute; bottom:-138px; left:50%; transform:translateX(-50%); width:256px; height:260px;">
<img src="./spike.png" alt="Footer Image" style="width:100%; height:100%; object-fit:cover;"/>
</div>
</footer>
-->

<!--
<footer style="height:260px; overflow:hidden; position:relative;">
<div style="position:absolute; top:-138px; left:50%; transform:translateX(-50%); width:256px; height:260px;">
<img src="./spike.png" alt="Footer Image" style="width:100%; height:100%; object-fit:cover;"/>
</div>
</footer>
-->
