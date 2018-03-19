Cortege: a Row-polymorphic Tuple
================================

<center>Draft</center>



Every once in a while I stumble upon some tuple-heavy code
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

Let's employ our wishful thinking an imagine how they might
look like.  OCaml row-polymorphic object type may look like this:

```ocaml
< width : int; height : int; ..>
```

Where the implicit row variable (`..`) tells us that
more fields are allowed. So why can't we say the same about
tuples? Let's use banana brackets for our imaginary
row-polymorphic tuple.

* `(| |)` would be a unit tuple;
* `(| 'a |)` would be a one-tuple;
* `(| 'a, 'b |)` would be a two-tuple;
* `(| 'a, .. |)` would be a tuple with at least one
  element, possibly more;
* `(| 'a, 'b, .. |)` with at least two elements, possibly more;
* `(| .. |)` would be a possibly empty tuple

Then you could write a selector function for the first
element that would work for any tuple with at least
one element:

```ocaml
val first : (| 'a, .. |) -> 'a
```

And other similar polymorphic accessor functions:

```ocaml
val second : (| _, 'a, .. |) -> 'a
val third  : (| _, _, 'a, .. |) -> 'a
```

Or polymorphic update functions:

```ocaml
module Update : sig
  val first  : 'x -> (| 'a, .. |) -> (| 'x, .. |)
  val second : 'x -> (| 'a, 'b, .. |) -> (| 'a, 'x, .. |)
  val third  : 'x -> (| 'a, 'b, 'c, .. |) -> (| 'a, 'c, 'x, .. |)
end
```

Why not a polymorphic prepend function?

```ocaml
val prepend : 'a -> (| .. |) -> (| 'a, .. |)
```



