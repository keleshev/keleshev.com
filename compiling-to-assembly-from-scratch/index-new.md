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
<a class="big-round-btn" href="https://www.lulu.com/shop/vladimir-keleshev-and-katiuska-pino/compiling-to-assembly-from-scratch/hardcover/product-579gk7z.html" style="width:230px; margin-left:75px">
  <center>
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
  </center>
</a>
<a href="#Contents" class="big-round-btn-inverted" style="width:230px; margin-left:74px;">
  <center>
    <table>
      <tr>
        <td><center>Read online for <b>free<b></center></td>
      </tr>
      <tr>
      </tr>
    </table>
  </center></a></div>

<!--<p>&nbsp;</p>-->

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

<span id="Contents"></span>


<h2>Contents</h2>

1. [Introduction](./)
2. [TypeScript Basics](./)

*Part I: Baseline Compiler*

3. [High-level Compiler Overview](./)
4. [Abstract Syntax Tree](./)
5. [Introduction to Parser Combinators](./)
6. [First Pass: The Parser](./)
7. [Introduction to ARM Assembly Programming](./)
8. [Second Pass: Code Generation](./)

*Part II: Compiler Extensions*

9. [Introduction to Part II](./)
10. [Primitive Scalar Data Types](./)
11. [Arrays and Heap Allocation](./)
12. [Visitor Pattern](./)
13. [Static Type Checking and Inference](./)
14. [Dynamic Typing](./)
15. [Garbage Collection](./)

*Appendices*

<ol type="A">
 <li>
   [Running ARM Programs](./)
 </li>
 <li>
   [GAS v. ARMASM Syntax](./)
 </li>
</ol>






<center><img src=/keleshev.jpg width=200 height=200 style="float:right; border-radius:200px; margin-top:50px" /></center>
## About me

My name is Vladimir Keleshev,
I have worked with compilers both commercially
and in open-source.
My fondness of ARM assembly stems from
my previous work in embedded systems.
Currently, I work in finance
with domain-specific languages.

## Questions? Comments? Feedback?

 * Email me at [vladimir@keleshev.com](mailto:vladimir@keleshev.com),
 * DM me at <a href="https://twitter.com/keleshev">@keleshev</a>, or
 * Open an issue or a pull request on [GitHub](https://github.com/keleshev/keleshev.com/tree/main/compiling-to-assembly-from-scratch).

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


<footer style="height:122px; overflow: hidden; position:relative;">
  <center style="pposition:absolute; overflow:visible;">
    <img style="object-fit:cover;" src=./spike.png width=256 height=260 />
  </center>
</footer>


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
