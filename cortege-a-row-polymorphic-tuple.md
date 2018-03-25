Cortege: a Row-polymorphic Tuple
================================

<center>2018-03-25</center>



Every once in a while I stumble upon some tuple code
[like this][ocaml-fst]:

```ocaml
let fst3 (x,_,_) = x
let snd3 (_,x,_) = x
let thd3 (_,_,x) = x

let fst4 (x,_,_,_) = x
let snd4 (_,x,_,_) = x
let thd4 (_,_,x,_) = x
let for4 (_,_,_,x) = x
```

Or even [like this][hackage-tuple]:

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
<span style='background: lightgrey'>...</span>
```

[ocaml-fst]: https://github.com/ocaml/ocaml/blob/7d5e40c102792001cd240e38c70c241fafff2d99/utils/misc.ml#L381-L388

[hackage-tuple]: https://hackage.haskell.org/package/tuple-0.3.0.2/docs/src/Data-Tuple-Update.html#Upd1


It always made me wonder if we could do better.
Couldn't we come up with a more polymorphic tuple type
for which we could write select, update, and other
functions without the need to duplicate the implementation
for each tuple size?!

There seems to be a gap in our type systems.
We have nominal variants, and their counterparts, row-polymorphic
variants. We have nominal records and row-polymorphic records.
We have tuples. So where are all the row-polymorphic tuples?!

Let's employ our wishful thinking and imagine how they might
look like.

## Bananan Notation

OCaml row-polymorphic object type may look like this:

```ocaml
< width : int; height : int; .. >
```

The implicit row variable (`..`) tells us that
more fields are allowed. So why can't we say the same about
tuples? Let's use banana brackets for our imaginary
row-polymorphic tuple:

* `(| 'a, 'b |)` would be a two-tuple;
* `(| 'a |)` would be a one-tuple;
* `(| |)` would be a unit tuple;
* `(| 'a, 'b, .. |)` would be a tuple with two elements, possibly more;
* `(| 'a, .. |)`—with at least one element, possibly more;
* `(| .. |)` would be a possibly empty tuple.

Then you could write selector functions
that work for any such tuple of appropriate size.
For example, accessor function for the first element
would require a tuple of size one or more:

```ocaml
val first  : (| 'a, .. |) -> 'a
val second : (| _, 'a, .. |) -> 'a
val third  : (| _, _, 'a, .. |) -> 'a
```

Similar story with polymorphic update functions:

```ocaml
module Update : sig
  val first  : 'x -> (| 'a, .. |) -> (| 'x, .. |)
  val second : 'x -> (| 'a, 'b, .. |) -> (| 'a, 'x, .. |)
  val third  : 'x -> (| 'a, 'b, 'c, .. |) -> (| 'a, 'c, 'x, .. |)
end
```

As well as other polymorphic functions:

```ocaml
val prepend : 'a -> (| .. |) -> (| 'a, .. |)
val swap : (| 'a, 'b, .. |) -> (| 'b, 'a, .. |)
val tail : (| 'a, .. |) -> (| .. |)
```

I am a little fast-and-loose with notation here.
We would probably need to make row variables explicit
to be able to say that they unify on both sides of an arrow:

```ocaml
val tail : (| 'a, .. as 'row |) -> (| .. as 'row |)
```

So what is stopping us from having such row-polymorphic tuples
in a language like OCaml?! Nothing, really!

## GADT Cortege

Here's _cortege_: a row-polymorphic tuple, implemented here using GADT:

```ocaml
module Cortege = struct
  type _ t =
    | [] : unit t
    | (::) : 'a * 'b t -> ('a -> 'b) t
end
```

At value-level, it is a simple linked list.
We also encode the type of each tuple element inside a type-level linked list.
We could use any type-level linked list, for example:

```ocaml
type nil
type ('head, 'tail) cons
```

However, we instead use the `unit` for nil and `(->)` for cons.
Unit type corresponds neatly to our unit cortege, while
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
to overload the list notation. We use this inside the cortege module
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

And check that they work on any sufficiently wide cortege:

```ocaml
assert Cortege.(first [true] = true);
assert Cortege.(first [true; "b"] = true);
assert Cortege.(first [true; "b"; `c] = true);
```

Notice that one-tuple is allowed.
Not sure if it is good or not.

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

While with the GADT cortege we gained a more polymorphic tuple type,
we lost our ability to represent a tuple with a flat array.

But with a little bit of "magic" and unsafe casting
we can re-gain our flat array representation:

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
```ocaml

```

We declare this cortege to be an abstract type backed by an int array.
But behind the compiler's back,
we unsafely coerce the values using `Obj.magic` to fit
our heterogeneous values into the array. To understand why this works
it is useful to know how [OCaml represents values at runtime][RWO].

[RWO]: https://realworldocaml.org/v1/en/html/memory-representation-of-values.html

We use the same type
parameter structure as we did with GADT to track the types of the contained
values, however, in this case, the type parameter is purely
a phantom type.

We can even use the faster `Array.unsafe_get`
and `Array.unsafe_set` in our implementation (which avoid bound checks),
because we have encoded the information about the number of
elements in a cortege using the phantom type.

At the end of the day, consider this implementation
a proof-of-concept that a cortege can be backed by a flat array,
but not something useful in practice (unlike the GADT version).
Notably, the `Array_backed_cortege` fails in unsafe ways whenever
floats are stored in it, because of OCaml's special representation
for float arrays.
We could take that into account and fix the code,
but I would still consider it to be
unpractical without the "literal" notation and pattern matching.




## Right? Left? Both!

We have now established that a row-polymorphic tuple can be expressed
in OCaml type system and that it could be backed by
a flat array. However, if it is a flat array, and not a linked list,
why limit ourselves
to representing the "tail" of the tuple as the row type?
Why not the start of the tuple? Why not both?

The row variable can stand for an unknown number of elements at
any position of the tuple: start, middle, or tail:

* `(| 'a, 'b, .. |)` is a cortege with at least two elements, possibly
  more on the right;
* `(| .., 'a, 'b |)` would be a cortege with at least two elements, possibly
  more on the left;
* `(| 'a, .., 'b |)`—with two elements, possibly more in the middle.

We could write accessors for last elements:

```ocaml
val last : (| .., 'a |) -> 'a
val last_but_one : (| .., 'a, _ |) -> 'a
```

Update functions alike. Or consider a swap function that swaps
the first and the last
element of any cortege, size two or more:

```ocaml
val swap : (| 'a, .., 'b |) -> (| 'b, .., 'a |)
```

<!--
Not completely sure if it would makes sense in general
to have more than one tow variable: `(| 'a, .., 'b, .., 'c |)`.
But perhaps this could be useful to concatenate two tuples:

```ocaml
val append : (| .. as 'r1 |) -> (| .. as 'r2 |) -> (| .. as 'r1, .. as 'r2 |)
```
-->


## Alternatives

Cortege is a solution to the problem of tuples being not flexible
and not polymorphic enough.
However, it could be that we are trying to solve the wrong problem.

Consider Elm, it limits tuples to at most a three-tuple and thus forces the user
to switch to a row-polymorphic record instead.
PureScript doesn't have built-in support for tuples at all in the language,
also on purpose.

A counterargument could be that, unlike row-polymorphic records,
corteges have a notion of order, so would fit well with applications
where the order is important. For example, a list of corteges can
model tabular data, like a CSV file, without losing the information
about the column order.

Another argument is that a Cortege could be implemented as a flat array,
unlike a row-polymorphic record.

So it could be that the cortege is a language feature that overlaps too much
with other features, like row-polymorphic records.
Or it could be a useful practical tool, who knows.
I recommend trying to use the GADT cortege for yourself, and over time
together we'll learn if it is any good.

## Code

Code from this article is available in [a GitHub gist][gist].

[gist]: https://gist.github.com/keleshev/321294ef84ceef475ddae85809c283e4

## Name

_Cortege_ or _кортеж_ is a French-borrowed Russian word for a tuple.

## Aknowledgements

Heterogeneous linked lists, like the GADT cortege, are not a new
idea. One reference to it I could find was in
[an OCaml compiler pull request](https://github.com/ocaml/ocaml/pull/234).

Thanks to my colleague Kristian Støvring for a valuable discussion
and for suggesting to use GADT for row-polymorphic tuples.  [&#9632;](/ "Home")

<center markdown="1">

⁂

<em>Follow me on <a href="http://twitter.com/keleshev">Twitter</a></em>
</center>


