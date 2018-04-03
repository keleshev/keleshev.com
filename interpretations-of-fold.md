Interpretations of Fold
=======================

<center style="margin-top: -1em"><em>or<br/> Fold as a Recursion Scheme</em> </center>



It is hard to remember the parameters of fold.

## First Interpretation
One interpretation of fold is that it is a way to
apply an operation "between" each two elements in a list.
Fold-right applies them in a right-associative manner:

```ocaml
List.fold_right (^) ["a"; "b"; "c"] "z"
 ⇒ ("a" ^ ("b" ^ ("c" ^ "z")))
```

Fold-left applies them in a left-associative manner:

```ocaml
List.fold_left (^) "z" ["a"; "b"; "c"]
 ⇒ ((("z" ^ "a") ^ "b") ^ "c")
```

It is hard to remember the parameters of fold.

OCaml standard library has [`StdLabels` module][stdlabels]
with labeled versions of functions, which helps:

[stdlabels]: http://caml.inria.fr/pub/docs/manual-ocaml/libref/StdLabels.List.html

```ocaml
let open StdLabels in
List.fold_right ~init:"z" ~f:(^) ["a"; "b"; "c"]
 ⇒ ("a" ^ ("b" ^ ("c" ^ "z")))
```

Jane Street [Base](https://opensource.janestreet.com/base/)
uses the same labeled parameters.

Still, it is hard to remember the parameters of fold.
Does `~f` take the accumulator first, or a list item?

## Second Interpretation

Another interpretation of fold is that it is a recursion
scheme with each parameter being a callback for each
variant constructor.

Let me explain. First, let's revisit the list type:

```ocaml
type 'a list =
  | []
  | (::) of 'a * 'a list
```

Nil constructor (`[]`) takes no parameters.
Cons constructor `(::)` takes two parameters:
an element of the list and the tail.

Now consider `fold_right` signature:

```ocaml
val fold_right : f:('a -> 'b -> 'b) -> 'a list -> init:'b -> 'b
```

The `init` parameter is a value (takes no parameters).
While `f` takes two parameters: an element of a list
and the result of applying the fold to a tail of a list.

The correspondence between the two parameters of fold
and the two list constructors is clear when
you look at the implementation:

```ocaml
let rec fold_right ~init ~f = function
  | [] -> init
  | head :: tail -> f head (fold_right ~init ~f tail)
```

The fold recurses on the tail parameter similar to
how the list type definition is recursive in the tail
parameter.

Let's rename the parameters to make the relation
between parameters and constructors even more clear:

```ocaml
let rec fold ~nil ~cons = function
  | [] -> nil
  | head :: tail -> cons head (fold ~nil ~cons tail)
```

We use `nil` value for the nil constructor,
`cons` callback for the cons constructor.
Fold is called recursively on the parameter that
is recursive in the type definition.
The fold is dual to the type.

*Then how do you explain fold-left?*

Fold-right is the _natural_ fold for list, dual to the type.
Fold-left is an unnatural
fold for list. It is a fold that pretends that the list
type is defined as left-heavy tree, as opposed to
a standard right-heavy tree. It pretends that
the cons constructor takes `'a list * 'a` instead
of `'a * 'a list`. Sometimes it is useful to pretend.

## Example I: Binary Tree

The power and generality of fold is very well known
for lists. Now you can get the same power for any variant data type.

Let's define a binary tree, a natural fold for it,
and then implement a few functions using the fold.

First the type:

```ocaml
type 'a t =
  | Leaf of 'a
  | Node of 'a t * 'a t
```

Now the fold:

```ocaml
let rec fold ~leaf ~node = function
  | Leaf a -> leaf a
  | Node (left, right) ->
      node (fold ~leaf ~node left) (fold ~leaf ~node right)
```

The fold recurses on both branches, similar to how the
type is defined as recursive on both node parameters.

> ## The Recipe
>
> Here's how to define a natural fold for your variant type.
>
> Fold takes one "callback" parameter for each variant.
> Labelled parameters work best for this.
>
> Patter match on your variant type. For each variant constructor pattern
> call the corresponding callback with the payload of each
> variant constructor, if any. One exception to that are the recursive
> values. For those, recursively call fold with the same callback parameters.
>

Let's define functional constructors. They will get
handy later.

```ocaml
let leaf a = Leaf a
let node left right = Node (left, right)
```

The size of a tree is a sum of sizes of each node,
whereas a leaf node counts as one (regardless of the value):

```ocaml
let size = fold ~leaf:(fun _ -> 1) ~node:(+)
```

The height of a singe leaf is one (regardless of the value),
while the height of a node is one more than the height of
its heighest branch:

```ocaml
let height =
  fold ~leaf:(fun _ -> 1) ~node:(fun a b -> 1 + max a b)
```

Let's define `to_string` function which serializes
a tree as an s-expression. As a parameter it takes
a function that knows how to serialize a leaf value.
We pass this parameter with label punning:

```ocaml
let to_string leaf = fold ~leaf ~node:(sprintf "(%s %s)")
```

Let's define and observe the relation between `map`,
`bind`, and `iter`. The map uses the `leaf` constructor
which we defined previously. Both the map and the bind
pass the `node` constructor with label punning.

```ocaml
let map f = fold ~leaf:(f >> leaf) ~node
let bind f = fold ~leaf&#58;f ~node
let iter f = fold ~leaf&#58;f ~node:(fun _ _ -> ())
```

Finally, `for_all` and `exists`:

```ocaml
let for_all predicate = fold ~leaf&#58;predicate ~node:(&&)
let exists predicate = fold ~leaf&#58;predicate ~node:(||)
```

Not all of these functions are efficient.
For example, in a strict language like OCaml, by passing `(&&)` and `(||)` to
`for_all` and `exists` (as opposed to inlining them)
we lost the short-circuiting power.
However, the natural fold allowed us to quickly
build a lot of functionality, and it reveals
interesting relations between the functions that we
implement.


## Example II: Compiler Pass

Let's re-implement the dead code elimination pass from the
[previous post][map-post], while using fold as our recursion
scheme, instead of map.

[map-post]: ./map-as-a-recursion-scheme-in-ocaml

First we implement fold by following the recipe.
Then the pass itself:

```ocaml
module Dead_code_elimination = struct
  open Syntax

  let pass =
    fold ~unit ~boolean ~number ~id
         ~divide ~sequence ~let_ ~if_:(function
      | {conditional=Boolean true; consequence; _} ->
          consequence
      | {conditional=Boolean false; alternative; _} ->
          alternative
      | other -> If other)
end
```

All the punned labled parameters look kinda funny.
We could have made them optional with default
implementations, but then the fold type would be more
monomorphic, being able to only return the same type it
folds on.

For comparison, here is original code:

```ocaml
module Dead_code_elimination = struct
  open Syntax

  let rec pass = function
    | If {conditional=Boolean true; consequence; _} ->
        pass consequence
    | If {conditional=Boolean false; alternative; _} ->
        pass alternative
    | other -> map pass other
end
```

Notice how in case of fold we did not need to recursively
apply the pass, as the fold does it for us.
On one hand, this saves us from mistakes:
we can't accidentally forget to recur in one of the
branches. On the other hand, we loose some control:
ability to get access to a value both before and
after the transformation, and ability *not* to
recur.

## Summary

Fold is a powerful recursion scheme and an elegant
tool that allows to quickly implememnt a rich
programming interface for a variant type.

Both natural folds and unnatural folds are useful.
Similar to how list implements natural `fold_right`
and unnatural `fold_left`, for my variant types
I would often implement a natural fold called `fold`
with labelled parameters, and one or more
unnatural folds, like `fold_right` that pretends
to fold a list. Often folds are useful for non-variant
types too, like `Array.fold_right` that
pretends that it folds a list.

## Code

Full code, including the ommitted pieces for the compiler pass
is avaialbe in a [GitHub gist][gist].  [&#9632;](/ "Home")

[gist]: https://gist.github.com/keleshev/36ea8fd1cd27995807ab49c4da04cc67


<center markdown="1">

⁂

<em>Discuss on <a href="https://twitter.com/keleshev/">Twitter</a></em>
</center>


