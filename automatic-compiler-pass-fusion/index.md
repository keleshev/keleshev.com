---
title: Automatic Compiler Pass Fusion
---

<style> #home { position: absolute; line-height: inherit; } </style>

<span id=home><a title=Home href=/>☰</a></span>

<h1>Automatic Compiler Pass Fusion</h1>

<center>2019-09-22</center>




On the one hand, when we write a compiler we want to split it into many
compiler passes to make each pass more tractable and testable. On the other
hand, we want to minimize the number of AST traversals to improve performance.
Automatic pass fusion is about combining several passes into one traversal to
address both concerns. This article presents one way to do that.

A previous post,
[map as a recursion scheme](./map-as-a-recursion-scheme-in-ocaml),
showed how to use the map function
to reduce boilerplate when writing compiler passes. In this post, we build upon
that work, including the toy language and the AST type, that we refer here as
`t`.

The language is as follows:

<p style="padding-left: 3.0em; text-indent: -1.25em" >
<em>e&nbsp;</em> → <code>(</code><em>e</em><code>)</code><br/>
  |<code> ()</code> <br/>
  |<b><code> true </code></b>|<b><code> false</code><br/> </b>
  |<code> 0 </code>|<code> 1 </code>|<code> 2 </code>|<code> </code>…<br/>
  |<code> </code><em>id</em><br/>
  |<code> </code><em>e</em><code> / </code><em>e</em><br/>
  |<code> </code><em>e</em><code>; </code><em>e</em><br/>
  |<b><code> let </code></b><em>id</em><code> = </code><em>e</em><b><code> in </code></b><em>e</em><br/>
  |<b><code> if </code></b><em>e</em><b><code> then </code></b><em>e</em><b><code> else </code></b><em>e</em>
</p>

Here is the type we use to represent its syntax:


```ocaml
type t =
  | Unit
  | Boolean of bool
  | Number of int
  | Id of string
  | Divide of t * t
  | Sequence of t * t
  | Let of {id: string; value: t; body: t}
  | If of {conditional: t; consequence: t; alternative: t}
```

## Overview

We’ll take three language transformations to create motivation for our passes.
Then we’ll implement them in three different ways:

 * First, as three separate passes doing three traversals.
 * Then, as one pass that is fused manually.
 * Last, we’ll try our automatic fusion technique.

As we go, we’ll compare the code, and in the end, we’ll compare the performance
too.

## Transformations

> If you’ve read this blog before, then you are familiar with these
> transformations. We've used them before.

Our first transformation is *dead code elimination*. It removes redundant
branches of the if statement, in case the condition is hard-coded:

```ocaml
if true  then x else y  ⇒  x
if false then x else y  ⇒  y
```

Next one is *constant propagation* where we compute statically
known fractions, for example:

```ocaml
42 / 2  ⇒  21
```

Next is *removing redundant let*, in case a let binding is
used immediately in its own body:

```ocaml
let x = y in x  ⇒  y
```

## No Fusion

First, let's implement the three passes separately, using
the map function
as the recursion scheme.

```ocaml
module Not_fused = struct
  module Dead_code_elimination = struct
    let rec pass = function
      | If {conditional=Boolean true; consequence; _} ->
          pass consequence
      | If {conditional=Boolean false; alternative; _} ->
          pass alternative
      | other ->
          map pass other
  end

  module Constant_propagation = struct
    let rec pass = function
      | Divide (Number n, Number m) when m <> 0 ->
          pass (Number (n / m))
      | other ->
          map pass other
  end

  module Remove_redundant_let = struct
    let rec pass = function
      | Let {name; value; body=Name n} when n = name ->
          pass value
      | other ->
          map pass other
  end

  let pass t =
    Remove_redundant_let.pass
      (Constant_propagation.pass
        (Dead_code_elimination.pass t))
end
```
```ocaml

```

In the end, we combined the passes using function composition.

## Manual Fusion

Now, let's try to combine the three passes into a single traversal manually.

```ocaml
module Manually_fused = struct
  let rec pass = function
    | If {conditional=Boolean true; consequence; _} ->
        pass consequence
    | If {conditional=Boolean false; alternative; _} ->
        pass alternative
    | Divide (Number n, Number m) when m <> 0 ->
        pass (Number (n / m))
    | Let {name; value; body=Name n} when n = name ->
        pass value
    | other ->
        map pass other
end
```

Note that `Not_fused.pass` and `Manually_fused.pass` are not the same
function. Since `Not_fused.pass` works in three separate passes, an earlier
pass might uncover more optimization opportunities for the next passes.
For example, consider a syntax tree corresponding to a fragment of our
toy language:

```ocaml
10 / (if true then 2 else 5)
```

The `Not_fused.pass` will first run `Dead_code_elimination.pass` to obtain
`10 / 2`, and then separately run `Constant_propagation.pass` to get the
result—`5`. At the same time, `Manually_fused.pass` dives straight into
dead code elimination, without reconsiderations and ends up with `10 / 2`
as the result.

However, both functions are not perfect and do not uncover all the
optimization opportunities. For example, consider a syntax tree for
the following fragment:

```ocaml
10 / (let x = 2 in x)
```

Both `Not_fused.pass` and `Manually_fused.pass` evaluate this to `10 / 2`.
So both miss some optimizations, and the only way to cover them all is to
call the function repeatedly until a fixpoint value emerges.

## Automatic Fusion

Here's an implementation style that allows writing the three passes separately,
and then fuse them into a single traversal.

```ocaml
module Fused = struct
  module Dead_code_elimination = struct
    let pass first_pass next_pass = function
      | If {conditional=Boolean true; consequence; _} ->
          first_pass consequence
      | If {conditional=Boolean false; alternative; _} ->
          first_pass alternative
      | other ->
          next_pass other
  end

  module Constant_propagation = struct
    let pass first_pass next_pass = function
      | Divide (Number n, Number m) when m <> 0 ->
          first_pass (Number (n / m))
      | other ->
          next_pass other
  end

  module Remove_redundant_let = struct
    let pass first_pass next_pass = function
      | Let {name; value; body=Name n} when n = name ->
          first_pass value
      | other ->
          next_pass other
  end

  (* Fuse the passes together *)
  let rec pass t =
    (Dead_code_elimination.pass pass
      (Constant_propagation.pass pass
        (Remove_redundant_let.pass pass
          (map pass)))) t
end
```
```ocaml

```

Here, each sub-pass, instead of being directly recursive, relies on open
recursion. Each takes two parameters: `first_pass` and `next_pass`. If none of
the patterns in the pass match, then it delegates the work to the `next_pass`.
However, if the pass needs to recur on a nested expression, it calls
`first_pass`, to re-start the pipeline.

The sub-passes are combined as follows. Each consecutive pass is the next one's
`next_pass` argument, ending with `map pass` which ties the first recursive knot.
The combined pass is also recursively passed to each function as the `first_pass`
parameter, tying the second recursive knot.

Fixpoint combinator and function composition operator could be
used here, but they affect the performance of the resulting
pass (probably due to closure allocation after partial application).

## Proof

The resulting function `Fused.pass` is identical to `Manually_fused.pass`
for all inputs. We can use [Imandra](https://www.imandra.ai/)
proof assistant to check this:

```ocaml
#use "fusion.ml"

theorem our_fusion_is_the_same_as_manual_fusion x =
  Fused.pass x = Manually_fused.pass x
[@@auto]
```

When running this, Imandra will print several pages of proofs,
and in the end will conclude:

```
[✓] Theorem proved.
```

## Benchmark

After generating `100_000_000` random syntax trees and measuring
the total time of applying the three different techniques, we get the
results in seconds:

<br/>
<center><img src=bench.svg></center>

<!--
* `Not_fused.pass`—11.803 seconds
* `Manually_fused.pass`—4.669 seconds
* `Fused.pass`—6.337 seconds-->

## Conclusion

We can see that our pass fusion technique achieves most of
the performance benefit of manual pass fusion, while maintaining
independent implementation of each sub-pass.

Having independent sub-passes allows a hypothetical pass manager
to arrange them differently, depending on the optimization level.
For a fast unoptimized build, it can fuse as many passes as possible
into one pipeline. For slower optimized builds it can instantiate
each sub-pass into a full-fledged pass and even run some of them
repeatedly.

Another benefit is that each sub-pass can be tested in isolation.

## Code

The [gist](https://gist.github.com/keleshev/3529129da1bd03b4e9e3e983434cedd8)
contains the code from this article together with additional
testing and benchmarking code.

## Futher work

All passes that we discussed have the form `t -> t`.
It would be interesting to see how this technique fairs
for passes of form `t -> t m` for some monad `m`, or for passes
from one AST to a different one.

The passes we discussed used disjoint patterns.
It would be interesting to see if this could be adapted for
passes with overlapping patterns.  [&#9632;](/ "Home")

[gist]: https://gist.github.com/keleshev/36ea8fd1cd27995807ab49c4da04cc67


<center markdown="1">

⁂

<em>Follow me on <a href="https://twitter.com/keleshev/">Twitter</a></em>
</center>


