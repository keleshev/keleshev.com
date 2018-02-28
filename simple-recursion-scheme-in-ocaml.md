Simple Recursion Scheme in OCaml
================================

<center>Draft</center>

Let us explore a simple recursion scheme in OCaml.
To create a motivation for it, and as an example, we will write a few
simple compiler passes for a toy language.

> You might think—*oh, crickets! again these functional programmers
> with their compilers*—as opposed to real problems.
> But I will interject.
> First, compilers are the single most researched application of software,
> so there is existing terminology which can be quickly used to
> build up a realistic example.
> Second, and more importantly, it looks like there are more and more
> applications of compiler construction methods to other fields,
> for example, [financial instruments][FI].
> It even may be that every software problem is a compiler problem.

[FI]: https://www.microsoft.com/en-us/research/wp-content/uploads/2000/09/pj-eber.pdf

Let's say we have the following informally specified language:

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

We can represent it straightforwardly with this type:

```ocaml
module Syntax = struct
  type t =
    | Unit
    | Boolean of bool
    | Number of int
    | Name of string
    | Divide of t * t
    | Sequence of t * t
    | Let of {name: string; value: t; body: t}
    | If of {conditional: t; consequence: t; alternative: t}
end
```
```ocaml

```

## 1. Primitive recursion

Now, let's say you want to eliminate dead code by creating
a compiler pass for the following transformation:

```ocaml
if true then x else y ⇒ x
if false then x else y ⇒ y
```

And here is how you can do it using primitive recursion:

```ocaml
module Dead_code_elimination = struct
  let rec pass = function
    | Unit | Boolean _ | Number _ | Name _ as t ->
        t
    | Divide (left, right) ->
        Divide (pass left, pass right)
    | Sequence (left, right) ->
        Sequence (pass left, pass right)
    | Let {name; value; body} ->
        Let {name; value=pass value; body=pass body}
    | If {conditional=Boolean true; consequence; _} ->
        pass consequence
    | If {conditional=Boolean false; alternative; _} ->
        pass alternative
    | If {conditional; consequence; alternative} ->
        let conditional = pass conditional in
        let consequence = pass consequence in
        let alternative = pass alternative in
        If {conditional; consequence; alternative}
end
```
```ocaml

```


## 2. Factored recursion

The problem with this solution is the following.
The highlighted area represents the actual transformation,
while the rest is boilerplate that makes sure that the
transformation is applied recursively.

This pattern can be captured by a `map` function that
applies a function `f` recursively to the data structure:

```ocaml
let map f = function
  | Unit | Boolean _ | Number _ | Name _ as t ->
      t
  | Divide (left, right) ->
      Divide (f left, f right)
  | Sequence (left, right) ->
      Sequence (f left, f right)
  | Let {name; value; body} ->
      Let {name; value=f value; body=f body}
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

Sum up:

* We can write several passes of the form `Syntax.t -> Syntax.t`
  and reuse a single `map` implementation to factor recursion.
* If we extend the `Syntax.t` type with new
  constructors, we will only need to modify `map`, without the
  need to modify each pass.
* If we find the need for it,
  we can modify `map` to be tail-recursive and all the passes
  using it will become tail-recursive for free.

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
passes of the form `Syntax.t -> Syntax.t`. We'll discuss it further.

## 3a. Recursion for free

So far the deal was that we can write `map` once
and then use it in several passes. However, if
your compiler has an intermediate representation with hundreds
of different nodes (like many do) it might be tedious to write.
Worse, what if you have many intermediate representations?

Fortunately, there is [`ppx_deriving`][DER] code generation
framework which can generate, among many others, a `map`
implementation for us, similar to Haskell's `deriving (Functor)`.

[DER]: https://github.com/ocaml-ppx/ppx_deriving

However, there's a caveat. Similar to `deriving (Functor)` in
Haskell, deriving a `map` implementation using `ppx_deriving`
requires a type with single type parameter: `'a t`.
We will need to rewrite our `Syntax.t` type to use a type
parameter instead of being defined self-referentially.
However, we'll be able to reclaim our monomorphic map in no time.
See here:

```ocaml
module Syntax = struct
  module Open = struct
    type 'a t = ❶
      | Unit
      | Boolean of bool
      | Number of int
      | Name of string
      | Divide of 'a * 'a
      | Sequence of 'a * 'a
      | Let of {name: string; value: 'a; body: 'a}
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
We'll refer to this type as "closed" type.

Unlike in Haskell, there is no need for a fix-point type and for
the wrapping and unwrapping that is associated with it.
OCaml supports such recursive type definitions using `-rectypes` compiler flag.
The resulting closed type `Syntax.t` is
undistinguishable from our original `Syntax.t`, for all intents and purposes.

We can also regain our monomorphic `map` ❹ function, if necessary,
by constraining `Open.map` with a signature.

Now we can write the same short version of dead code elimination pass without
writing the `map` function ourselves.

## Monads

So far we were only able to automate recursion for
passes of form `Syntax.t -> Syntax.t`.
What about passes that return an option?
A result type to signal errors?
And how about passes that need to maintain, say, a lexical environment?

Say, we want to write a pass of form `Syntax.t -> (Syntax.t, 'error) result`
that checks for literal division by zero.

Let's write it using primitive recursion first.
We'll use result monad to recursively compose our pass:

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
    | Unit | Boolean _ | Number _ | Name _ as t ->
        return t
    | Divide (_, Number 0) ->
        Error `Literal_division_by_zero
    | Divide (left, right) ->
        pass left >>= fun left ->
        pass right >>= fun right ->
        return (Divide (left, right))
    | Sequence (left, right) ->
        pass left >>= fun left ->
        pass right >>= fun right ->
        return (Sequence (left, right))
    | Let {name; value; body} ->
        pass value >>= fun value ->
        pass body >>= fun body ->
        return (Let {name; value; body})
    | If {conditional; consequence; alternative} ->
        pass conditional >>= fun conditional ->
        pass consequence >>= fun consequence ->
        pass alternative >>= fun alternative ->
        return (If {conditional; consequence; alternative})
end
```

As previously, the highlighted area shows the code that
implements the transformation, and the rest is boilerplate
that implements the recursion.

And like before, we can just factor that boilerplate out
and as a result, we get a `map_result` function
that maps from `Syntax.t -> (Syntax.t, 'error) result`:

```ocaml
open Result

let rec map_result f = function
  | Unit | Boolean _ | Number _ | Name _ as t ->
      return t
  | Divide (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Divide (left, right))
  | Sequence (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Sequence (left, right))
  | Let {name; value; body} ->
      f value >>= fun value ->
      f body >>= fun body ->
      return (Let {name; value; body})
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
    | Divide (_, Number 0) -> Error "`Literal_division_by_zero"
    | other -> map_result pass other
end
```
```ocaml

```

Much better now!

However, looking at `map_result` implementation we can
quickly discover that it has nothing specific to
`result` type. It only uses `return` and `bind`.
So, instead, we can make a "generator" function
which is parametrized over `return` and `bind` to
get a mapper for any monad:

```ocaml
let generate_map ~return ~bind:(>>=) f = function
  | Unit | Boolean _ | Number _ | Name _ as t ->
      return t
  | Divide (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Divide (left, right))
  | Sequence (left, right) ->
      f left >>= fun left ->
      f right >>= fun right ->
      return (Sequence (left, right))
  | Let {name; value; body} ->
      f value >>= fun value ->
      f body >>= fun body ->
      return (Let {name; value; body})
  | If {conditional; consequence; alternative} ->
      f conditional >>= fun conditional ->
      f consequence >>= fun consequence ->
      f alternative >>= fun alternative ->
      return (If {conditional; consequence; alternative})
```

What shall we do with it?

We can generate `map_result` from result monad to implement
our literal division checker:

```ocaml
let map_result = generate_map ~return:Result.return ~bind:Result.(>>=)

module Check_literal_division_by_zero = struct
  let rec pass = function
    | Divide (_, Number 0) -> Error "`Literal_division_by_zero"
    | other -> map_result pass other
end
```

We can generate `map_option` with option monad to get
`Syntax.t -> Syntax.t option` passes.

We can pass identity monad to get our original `map`
function and implement the dead code elimination pass:

```ocaml
let map = generate_map ~return:Identity.return ~bind:Identity.(>>=)

module Dead_code_elimination = struct
  let rec pass = function
    | If {conditional=Boolean true; consequence; _} ->
        pass consequence
    | If {conditional=Boolean false; alternative; _} ->
        pass alternative
    | other -> map pass other
end
```








* * *


TODO
====

 * http://blog.sumtypeofway.com/an-introduction-to-recursion-schemes/
 * mention tail recursion
 * no `-rectypes` for polymorphic variants
