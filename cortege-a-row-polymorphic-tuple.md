Cortege: a Row-polymorphic Tuple
================================

<center>Draft</center>



Every once in a while I stumble upon some tuple code
[like this](ocaml-fst):

```ocaml
let fst3 (x,_,_) = x
let snd3 (_,x,_) = x
let thd3 (_,_,x) = x

let fst4 (x,_,_,_) = x
let snd4 (_,x,_,_) = x
let thd4 (_,_,x,_) = x
let for4 (_,_,_,x) = x
...
```

Or even [like this](hackage-tuple):

```haskell
instance Upd1 b (a1,a2) (b,a2) where
  upd1 b (a1,a2) = (b,a2)
instance Upd1 b (a1,a2,a3) (b,a2,a3) where
  upd1 b (a1,a2,a3) = (b,a2,a3)
instance Upd1 b (a1,a2,a3,a4) (b,a2,a3,a4) where
  upd1 b (a1,a2,a3,a4) = (b,a2,a3,a4)
instance Upd1 b (a1,a2,a3,a4,a5) (b,a2,a3,a4,a5) where
  upd1 b (a1,a2,a3,a4,a5) = (b,a2,a3,a4,a5)
instance Upd1 b (a1,a2,a3,a4,a5,a6) (b,a2,a3,a4,a5,a6) where
  upd1 b (a1,a2,a3,a4,a5,a6) = (b,a2,a3,a4,a5,a6)
...
```

[ocaml-fst]: https://github.com/ocaml/ocaml/blob/7d5e40c102792001cd240e38c70c241fafff2d99/utils/misc.ml#L381-L388

[hackage-tuple]: https://hackage.haskell.org/package/tuple-0.3.0.2/docs/src/Data-Tuple-Update.html#Upd1


It always made me wonder if we could do better.
Couldn't we come up with a more polymorphic tuple type
for which we could write select, update, and other
functions without the need to duplicate the implementation
for each tuple type?!

There seems to be a gap in our type systems.
We have nominal variants, and their counterparts, row-polymorphic
variants. We have nominal records, and row-polymorphic records.
We have tuples. So where are all the row-polymorphic tuples?!

Let's employ our wishful thinking and imagine how they might
look like.

## Notation

OCaml row-polymorphic objects type look like this:

```ocaml
< width : int; height : int; .. >
```

Where the implicit row variable (`..`) tells us that
more fields are allowed. So why can't we say the same about
tuples? Let's use banana brackets for our imaginary
row-polymorphic tuple.

* `(| 'a, 'b |)` would be a two-tuple;
* `(| 'a |)` would be a one-tuple;
* `(| |)` would be a unit tuple;
* `(| 'a, 'b, .. |)` would be a tuple with two elements, possibly more;
* `(| 'a, .. |)` with at least one element, possibly more;
* `(| .. |)` would be a possibly empty tuple.

Then you could write a selector function for the first
element that would work for any tuple with at least
one element, and other polymorphic accessor functions:

```ocaml
val first  : (| 'a, .. |) -> 'a
val second : (| _, 'a, .. |) -> 'a
val third  : (| _, _, 'a, .. |) -> 'a
```

As well as polymorphic update functions:

```ocaml
module Update : sig
  val first  : 'x -> (| 'a, .. |) -> (| 'x, .. |)
  val second : 'x -> (| 'a, 'b, .. |) -> (| 'a, 'x, .. |)
  val third  : 'x -> (| 'a, 'b, 'c, .. |) -> (| 'a, 'c, 'x, .. |)
end
```

Why not some other polymorphic functions?

```ocaml
val prepend : 'a -> (| .. |) -> (| 'a, .. |)
val swap : (| 'a, 'b, .. |) -> (| 'b, 'a, .. |)
val tail : (| 'a, .. |) -> (| .. |)
```

I am a little bit fast-and-loose with notation here.
We would probably need to make row variables explicit
to be able to say that they unify on both sides of an arrow:

```ocaml
val tail : (| 'a, .. as 'row |) -> (| .. as 'row |)
```

So what is stopping us to have such row-polymorphic tuples
in a language like, say, OCaml?! Nothing, really!

## GADT Cortege

Here's Cortege: a row-polymorphic tuple, implemented using a GADT:

```ocaml
module Cortege = struct
  type _ t =
    | [] : unit t
    | (::) : 'a * 'b t -> ('a -> 'b) t
end
```

At value-level it is a simple linked list.
We encode the type of each tuple element inside a type-level linked list.
We could use any type-level linked list, for example:

```ocaml
type nil
type ('head, 'tail) cons
```

However we instead use `unit` for nil and `(->)` for cons.
Unit type corresponds neatly to our unit Cortege, while
the function type `(->)` is convenient because of the infix notation.


Here's the correspondence between our notation and the Cortege type:

```ocaml
(| 'a, 'b |)      ⇒  ('a -> 'b -> unit) Cortege.t
(| 'a |)          ⇒  ('a -> unit) Cortege.t
(| |)             ⇒  unit Cortege.t
(| 'a, 'b, .. |)  ⇒  ('a -> 'b -> 'row) Cortege.t
(| 'a, .. |)      ⇒  ('a -> 'row) Cortege.t
(| .. |)          ⇒  'row Cortege.t
```

Since OCaml version 4.03 we can re-define `[]` and `(::)` constructors
to overload the list notation. We use this inside of the Cortege module
to conveniently construct our row-polymorphic tuples:

```ocaml
let unit = Cortege.[]
let pair a b = Cortege.[a; b]
let triple a b c = Cortege.[a; b; c]
```

Let's define accessor functions:

```ocaml
let first  Cortege0.(x :: _) = x
let second Cortege0.(_ :: x :: _) = x
let third  Cortege0.(_ :: _ :: x :: _) = x
```

And check that they work on any sufficiently wide Cortege:

```ocaml
assert Cortege.(first [true] = true);
assert Cortege.(first [true; "b"] = true);
assert Cortege.(first [true; "b"; `c] = true);
```

We can also notice that Cortege allows for a one-tuple.
Not sure if it is a good or a bad thing.

Let's define update functions:

```ocaml
module Update = struct
  let first  x (a :: rest) = x :: rest
  let second x (a :: b :: rest) = a :: x :: rest
  let third  x (a :: b :: c :: rest) = a :: b :: x :: rest
end
```

Pattern matching works perfectly. We can both use
the list notation and the cons constructor in patterns:

```ocaml
assert begin
  match Cortege.[<b>true</b>; "a"; `b] with
  | Cortege.[<b>true</b>; _; _] -> true
  | Cortege.(false :: _) -> false
end
```
As well as our miscelaneous functions:

```ocaml
let prepend a rest = Cortege.(a :: rest)
let swap Cortege.(a :: b :: rest) = Cortege.(b :: a :: rest)
let tail Cortege.(_ :: rest) = rest
```

## Flat Cortege

While with Cortege we gained a more polymorphic tuple type,
we lost our ability to represent a tuple with a flat array.

However, with a little big of "magic" and unsafe casting
we can re-implement our Cortege with a flat array type:

```ocaml
module type CORTEGE = sig
  type _ t

  val unit : unit t
  val pair : 'a -> 'b -> ('a -> 'b -> unit) t
  val triple : 'a -> 'b -> 'c -> ('a -> 'b -> 'c -> unit) t

  val prepend : 'head -> 'tail t -> ('head -> 'tail) t

  val first  : ('a -> _) t -> 'a
  val second : (_ -> 'a -> _) t -> 'a
  val third  : (_ -> _ -> 'a -> _) t -> 'a

  <span style='background: lightgrey'>...</span>
end

module Array_backed_cortege : CORTEGE = struct
  type _ t = int array

  let unit = [||]
  let pair a b = [|Obj.magic a; Obj.magic b|]
  let triple a b c = [|Obj.magic a; Obj.magic b; Obj.magic c|]

  let prepend head tail = Array.append [|Obj.magic head|] tail

  let first  t = Obj.magic (Array.unsafe_get t 0)
  let second t = Obj.magic (Array.unsafe_get t 1)
  let third  t = Obj.magic (Array.unsafe_get t 2)

  <span style='background: lightgrey'>...</span>
end
```

We declare Cortege to be an int array, but behind the compiler's
back we unsafely coerce the values using `Obj.magic` to shape
our heterogeneous tuples as flat arrays. To know how this works
it is usefull to know how [OCaml represents values at runtime][RWO].

[RWO]: https://realworldocaml.org/v1/en/html/memory-representation-of-values.html

We use the same type
parameter structure as we did with GADT to track the types of the contained
values, however in this case the type parameter is purely
a phantom type.

We can even use the faster `Array.unsafe_get`
and `Array.unsafe_set` in our implementation (which avoid bounds checking),
because we have encoded the information about the number of
elements in a Cortege using types.

In the end of the day, consider this implementation
a proof-of-concept that a Cortege can be backed by a flat array.
Not something useful in practice, like the GADT version.
Notably, the `Array_backed_cortege` fails in unsafe ways whenever
floats are stored in it, because of OCaml's special representation
for float arrays.
This could be accounted for, but I would still consider it to be
unpractical without "literal" notation and pattern matching.
