Map as a Recursion Scheme in OCaml
==================================

<center>2018-03-15</center>

Let us explore a simple recursion scheme in OCaml.
To create motivation for it, we will write a few
simple compiler passes for a toy language.

> You might think—*oh, crickets! again these functional programmers
> with their compilers! gimme some real problems!*
>
> First, compilers are the single most researched application of software,
> so there is existing terminology which can be quickly used to
> build up a realistic example.
>
> Second, and more importantly, it looks like there are more and more
> applications of compiler construction methods to other fields,
> for example, [financial instruments][FI].
> It even may be that every software problem is a compiler problem.

[FI]: https://www.microsoft.com/en-us/research/wp-content/uploads/2000/09/pj-eber.pdf

Let's say we have the following informally specified language:

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

<!--
```ocaml
e → (e)
  | ()
  | true | false
  | 0 | 1 | 2 | …
  | id
  | e / e
  | e; e
  | let e = e in e
  | if e then e else e
```
-->

We can represent it straightforwardly with this type:

```ocaml
module Syntax = struct
  type t =
    | Unit
    | Boolean of bool
    | Number of int
    | Id of string
    | Divide of t * t
    | Sequence of t * t
    | Let of {id: string; value: t; body: t}
    | If of {conditional: t; consequence: t; alternative: t}
end
```
```ocaml

```

## 1. Primitive recursion

Now, let's say you want to eliminate dead code by creating
a compiler pass for the following transformations:

```ocaml
if true  then x else y  ⇒  x
if false then x else y  ⇒  y
```

And here is how you can do it using primitive recursion:

```ocaml
module Dead_code_elimination = struct
  let rec pass = function
    | Unit | Boolean _ | Number _ | Id _ as t ->
        t
    | Divide (left, right) ->
        Divide (pass left, pass right)
    | Sequence (left, right) ->
        Sequence (pass left, pass right)
    | Let {id; value; body} ->
        Let {id; value=pass value; body=pass body}
<div style='margin-left: -1.20em; background: lightgrey'>      | If {conditional=Boolean true; consequence; _} ->
          pass consequence
      | If {conditional=Boolean false; alternative; _} ->
          pass alternative
</div>    | If {conditional; consequence; alternative} ->
        let conditional = pass conditional in
        let consequence = pass consequence in
        let alternative = pass alternative in
        If {conditional; consequence; alternative}
end
```
```ocaml

```

The highlighted area represents the actual transformation,
while the rest is boilerplate that makes sure that the
transformation is applied recursively.

## 2. Factored recursion

This pattern of recursion can be captured by a `map` function that
applies a function `f` recursively to the data structure:

```ocaml
let map f = function
  | Unit | Boolean _ | Number _ | Id _ as t ->
      t
  | Divide (left, right) ->
      Divide (f left, f right)
  | Sequence (left, right) ->
      Sequence (f left, f right)
  | Let {id; value; body} ->
      Let {id; value=f value; body=f body}
  | If {conditional; consequence; alternative} ->
      let conditional = f conditional in
      let consequence = f consequence in
      let alternative = f alternative in
      If {conditional; consequence; alternative}
```

Now we can rewrite our compiler pass to focus on the
actual transformation and to delegate the recursive descent
to `map`:

```ocaml
module Dead_code_elimination = struct
  let rec pass = function
    | If {conditional=Boolean true; consequence; _} ->
        pass consequence
    | If {conditional=Boolean false; alternative; _} ->
        pass alternative
    | other -> map pass other
end
```
```ocaml

```
Now the pass is focused on the transformation.  To sum up:

* We can write several passes of the form `Syntax.t -> Syntax.t`
  and reuse a single `map` implementation to factor recursion.
* If we extend the `Syntax.t` type with new
  constructors, we will only need to modify `map`, without the
  need to modify each pass.
* If we find the need for it,
  we can modify `map` to be tail-recursive, and all the passes
  using it will become tail-recursive as well.

Caveat: our `map` implementation above is peculiar.
Instead of the regular signature:

```ocaml
val map : ('a -> 'b) -> 'a t -> 'b t
```

It has a monomorphic signature, where `'a`, `'b`, `'a t`, `'b t` are
the same thing:

```ocaml
val map : (Syntax.t -> Syntax.t) -> Syntax.t -> Syntax.t
```

Thus, this `map` will only help us factor out recursion for
passes of the form `Syntax.t -> Syntax.t`.
We'll see what we can do about other kinds of passes further.

## 3. Recursion for free

So far the deal was that we could write `map` once
and then use it in several passes. However, if
your compiler has an intermediate representation with hundreds
of different nodes (like many do), it might be tedious to write.
Worse, what if you have many intermediate representations?

Fortunately, there is [`ppx_deriving`][DER] code generation
framework which can generate, among many others, a `map`
implementation for us, similar to Haskell's `deriving Functor`.

[DER]: https://github.com/ocaml-ppx/ppx_deriving

However, there's a caveat. Similar to `deriving Functor` in
Haskell, deriving a `map` implementation using `ppx_deriving`
requires a type with a single type parameter: `'a t`.
We will need to rewrite our `Syntax.t` type to use a type
parameter instead of it being defined self-referentially.
However, we'll be able to reclaim our monomorphic map in no time.
See here:

```ocaml
module Syntax = struct
  module Open = struct
    type 'a t = ❶
      | Unit
      | Boolean of bool
      | Number of int
      | Id of string
      | Divide of 'a * 'a
      | Sequence of 'a * 'a
      | Let of {id: string; value: 'a; body: 'a}
      | If of {conditional: 'a; consequence: 'a; alternative: 'a}
      [@@deriving map] ❷
  end

  type t = t Open.t ❸

  let map: (t -> t) -> t -> t = Open.map ❹
end
```
```ocaml

```

<!--
<ol style="list-style: none; margin-left: 0; padding-left: 40; text-indent: -1em;">
  <li>❶ First, we called our new polymorphic type <code>'a Syntax.Open.t</code>.
We'll refer to it as an “open” type.</li>
  <li>❷ Second, we used the deriving framework to get <code>map</code> for free.</li>
  <li>❸ We regained our monomorphic type by making a recursive type definition.
We'll refer to this type as a “closed” type. Unlike Haskell,
OCaml has support for recursive types via <code>-rectypes</code> compiler option.</li>
  <li>❹ We regained our monomorphic <code>map</code> by constraining it with a signature,
but this is not strictly necessary.</li>
</ol>
-->

First, we called our new polymorphic type `'a Syntax.Open.t` ❶.
We'll refer to it as an "open" type.
Second, we used the deriving framework to get `map` for free ❷.
We regained our monomorphic type by making a recursive type definition ❸.
We'll refer to this type as a "closed" type.

Unlike in Haskell, there is no need for a fix-point type and for
the wrapping and unwrapping that is associated with it.
OCaml supports such recursive type definitions using `-rectypes` compiler flag.
The resulting closed type `Syntax.t` is
indistinguishable from our original `Syntax.t`, for all intents and purposes.

> Interestingly enough, `-rectype` flag is not necessary for tying
> the recursive knot when used together with polymorphic variants.
> And there might be more reasons to use polymorphic variants for
> syntax trees and intermediate representations.

We can also regain our monomorphic `map` ❹ function, if necessary,
by constraining `Open.map` with a signature.

Now we can write the same short version of the dead code elimination pass without
writing the `map` function ourselves.

## 4. Monadic passes

So far we were only able to automate recursion for
passes of form `Syntax.t -> Syntax.t`.
What about passes that return an option?
A result type to signal errors?
And how about passes that need to maintain a lexical environment?

Say, we want a pass of form `Syntax.t -> (Syntax.t, 'error) result`
that checks for literal division by zero.

Let's write it using primitive recursion first.
We'll use the result monad to compose our pass recursively.
Normally you would use a library like [Base.Result][Result]
for that, but let's spell it out here:

[Result]: https://ocaml.janestreet.com/ocaml-core/latest/doc/base/Base/Result/

```ocaml
module Result = struct
  let return x = Ok x

  let (>>=) = function
    | Ok ok -> fun f -> f ok
    | error -> fun _ -> error
end
```

And then we implement the pass itself:

```ocaml
module Check_literal_division_by_zero = struct
  let rec pass = function
    | Unit | Boolean _ | Number _ | Id _ as t ->
        return t
<div style='margin-left: -1.20em; background: lightgrey'>      | Divide (_, Number 0) ->
          Error `Literal_division_by_zero
</div>    | Divide (left, right) ->
        pass left >>= fun left ->
        pass right >>= fun right ->
        return (Divide (left, right))
    | Sequence (left, right) ->
        pass left >>= fun left ->
        pass right >>= fun right ->
        return (Sequence (left, right))
    | Let {id; value; body} ->
        pass value >>= fun value ->
        pass body >>= fun body ->
        return (Let {id; value; body})
    | If {conditional; consequence; alternative} ->
        pass conditional >>= fun conditional ->
        pass consequence >>= fun consequence ->
        pass alternative >>= fun alternative ->
        return (If {conditional; consequence; alternative})
end
```
```ocaml

```

As previously, the highlighted area shows the code that
implements the transformation, and the rest is boilerplate
that implements recursion.

> We have used a polymorphic variant <code>`Literal&lowbar;division&lowbar;by&lowbar;zero</code>
> for our error value. To learn why this might be a good idea read
> about [Composable Error Handling in OCaml](./composable-error-handling-in-ocaml).

Like we did before, we can factor the boilerplate out
and, as a result, we get `map_result`, a function
that maps `Syntax.t -> (Syntax.t, 'error) result`:

```ocaml
open Result

let rec map_result f = function
  | Unit | Boolean _ | Number _ | Id _ as t ->
      return t
  | Divide (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Divide (left, right))
  | Sequence (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Sequence (left, right))
  | Let {id; value; body} ->
      f value >>= fun value ->
      f body >>= fun body ->
      return (Let {id; value; body})
  | If {conditional; consequence; alternative} ->
      f conditional >>= fun conditional ->
      f consequence >>= fun consequence ->
      f alternative >>= fun alternative ->
      return (If {conditional; consequence; alternative})
```

We can convince ourselves that it works by rewriting the pass
with recursion delegated to `map_result`:

```ocaml
module Check_literal_division_by_zero = struct
  let rec pass = function
    | Divide (_, Number 0) ->
        Error `Literal_division_by_zero
    | other -> map_result pass other
end
```
```ocaml

```

Much better now!

However, looking at `map_result` implementation, we can
quickly discover that it has nothing specific to the
`result` type. It only uses `return` and `bind`.
So, instead, we can make a "map generator" function
which is parametrized over `return` and `bind` to
get a mapper for any monad:

```ocaml
let map_monad ~return ~bind:(>>=) f = function
  | Unit | Boolean _ | Number _ | Id _ as t ->
      return t
  | Divide (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Divide (left, right))
  | Sequence (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Sequence (left, right))
  | Let {id; value; body} ->
      f value >>= fun value ->
      f body >>= fun body ->
      return (Let {id; value; body})
  | If {conditional; consequence; alternative} ->
      f conditional >>= fun conditional ->
      f consequence >>= fun consequence ->
      f alternative >>= fun alternative ->
      return (If {conditional; consequence; alternative})
```

> One can write a `ppx_deriving` plugin to automatically
> derive this function, just like `map`.

What can we do with it?
We can use it to factor out recursion form any pass of the form`Syntax.t -> Syntax.t m` where `m` is a monad type.

We can generate `map_result` from result monad to implement
our literal division checker:

```ocaml
let map_result =
  map_monad ~return&#58;Result.return ~bind&#58;Result.(>>=)

module Check_literal_division_by_zero = struct
  let rec pass = function
    | Divide (_, Number 0) ->
        Error `Literal_division_by_zero
    | other -> map_result pass other
end
```
```ocaml

```
We can generate `map_option` with option monad to get
`Syntax.t -> Syntax.t option` passes.

We can pass identity monad to get our original `map`
function and implement the dead code elimination pass:

```ocaml
let map =
  map_monad ~return&#58;Identity.return ~bind&#58;Identity.(>>=)

module Dead_code_elimination = struct
  let rec pass = function
    | If {conditional=Boolean true; consequence; _} ->
        pass consequence
    | If {conditional=Boolean false; alternative; _} ->
        pass alternative
    | other -> map pass other
end
```
```ocaml

```

## 5. State monad pass

Some passes need to maintain a symbol table for lexical analysis.

Consider a pass that finds all variables which are undefined
according to the rules of lexical scope.
When recurring, it needs to pass down the list of variables available in scope,
and pass up the list of undefined variables that it found.

The following type can be used for this purpose:

```ocaml
module Environment = struct
  type t = {defined: string list; undefined: string list}

  let initial = {defined=[]; undefined=[]}
end
```
```ocaml

```

Since `map_monad` works for any monad, we could
define a state monad for `Environment.t` and use
it to factor out the recursive pattern.

When using a [monad library in OCaml][State Monad]
we can obtain a state monad from a type with no effort,
and get a rich set of functions to work with it:

[State Monad]: http://blogs.perl.org/users/cyocum/2012/11/writing-state-monads-in-ocaml.html

```ocaml
module Monad = StateMonad (Environment)
```

However, for illustrative purpose let's write a state monad
for `Environment.t` manually while keeping in mind that
we can get most of the code below for free:

```ocaml
module Monad = struct
  type 'a t = Environment.t -> 'a * Environment.t

  let return a env = a, env

  let (>>=) t callback env =
    let a, env = t env in
    callback a env

  let with_defined name t {defined; undefined} = ❶
    let a, env = t {undefined; defined=name :: defined} in
    a, {env with defined}

  let check_id name env = ❷
    if List.mem name env.defined then
      (), env
    else
      (), {env with undefined=name :: env.undefined}

  let undefined t = (snd (t initial)).undefined ❸
end
```
```ocaml

```

We have also written three functions that are specific
to our pass. Number ❶ is `with_defined` which
given an identifier adds it to the `defined` list
to pass this information down. Number ❷ is `check_id`.
Given an identifier it checks if it belongs to the `defined` list,
and if it does not—it adds it to the list of `undefined` variables.
Finally ❸ we create a function to extract the list of
undefined variables from a monadic value.

Now, we have everything in place to write our pass
that checks for undefined variables.

First, we generate `map_environment` that maps
`Syntax.t -> Sytax.t Environment.Monad.t`:

```ocaml
let map_environment =
  map_monad ~return&#58;Monad.return ~bind&#58;Monad.(>>=)
```

And now, the pass itself:

```ocaml
module Collect_undefined_variables = struct
  let rec pass = function
    | Let {id; value; body} ->
        pass value >>= fun value ->
        with_defined id (pass body) >>= fun body ->
        return (Let {id; value; body})
    | Id id as t ->
        check_id id >>= fun () ->
        return t
    | other -> map_environment pass other
end
```
```ocaml

```

When our pass reaches a let-binding, it
uses `with_defined` to pass down the information
about the bound identifier to the
body of the binding. If we had support for `let rec`
we would also use `with_defined` for the value branch.

When we reach an identifier, we check that it is
in scope using `check_id` function, and if it is not,
`check_id` will add it to the `undefined` list.

We delegate the recursion to `map_environment`.

Let us test this pass. Consider the following program in our toy language:

```ocaml
<span style='background: lightgrey'>x</span>;
let x = () in
let a = () in
a;
let b = a in
let y = <span style='background: lightgrey'>y</span> in
(let z = () in ());
a; b; <span style='background: lightgrey'>z</span>
```

The three variables highlighted are used outside
of the lexical scope where they are defined.

This program can be represented as the following syntax tree:

```ocaml
let tree =
  let (%) left right = Sequence (left, right) in
  Id "x" %
    Let {id="x"; value=Unit; body=
      Let {id="a"; value=Unit; body=
        Id "a" %
          Let {id="b"; value=Id "a"; body=
            Let {id="y"; value=Id "y"; body=
              Let {id="z"; value=Unit; body=Unit} %
                Id "a" % Id "b" % Id "z"}}}}
```

We write a test that applies our pass to the
tree and extracts the list of undefined variables
from the resulting value:

```ocaml
let () =
  let pass = Collect_undefined_variables.pass in
  assert (undefined (pass tree) = ["z"; "y"; "x"])
```

And confirm that they are `z`, `y`, and `x`.
If our syntax tree had location information we could easily
collect the precise locations of the undefined variables.

## Summary

* By using `map`, we can reuse the recursive
  pattern for `t -> t` passes.
* We can get a map for our type for free using `deriving map`.
* We can write a general map generator that automates
  recursion for `t -> t m` passes, for any monad `m`, notably for
    identity, option, result, and state monads.
* One can write a deriving plugin for the map generator, if necessary.

You can find the code from this article in [a GitHub gist](https://gist.github.com/keleshev/284c5dd9a74fea8efcd66d86e4109504) along with more tests
and examples that you can play with.

## Limitations and further steps

The approach of using a map function as a recursion scheme
works well when your pass works on a subset of variants
and ignores the rest. However, it does not offer anything
for the cases when a pass needs to touch every variant,
which is common. For these cases there are other recursive
schemes.

Not all passes map over the same syntax tree or intermediate
representation type. Many useful passes work by converting
one representation to a different one. In a future post we'll
explore what can be done for passes of form `a -> b m`,
for some `a` and `b`.

## Resources

[Adventures in Uncertainty](http://blog.sumtypeofway.com) is a blog
about recursion schemes in Haskell. [&#9632;](/ "Home")


<center markdown="1">

⁂

<em>Follow me on <a href="http://twitter.com/keleshev">Twitter</a></em>
</center>


