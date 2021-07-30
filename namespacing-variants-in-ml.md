---
title: "Namespacing Variants in ML"
fancy-title: "Namespacing Variants in ML"
date: 2015-04-12
cta: {book: yes}
---

When reading code written in OCaml or Standard ML,
I keep seeing variant constructors having ad-hoc prefixes
or suffixes used for namespacing.

Here's an example from
[Modern Compiler Implementation in ML][Appel] (page 98):

[Appel]: http://www.amazon.com/Modern-Compiler-Implementation-Andrew-Appel/dp/0521607647

```ocaml
type operator = PlusOp | MinusOp | TimesOp | DivideOp
```

And here's just one of many examples from [Facebook pfff tool][pfff]:

[pfff]: https://github.com/facebook/pfff/blob/master/lang_php/parsing/ast_php.ml#L138

```ocaml
type hint_type =
  | Hint of name * type_args option
  | HintArray of tok
  | HintQuestion of tok * hint_type
  | HintTuple of hint_type comma_list paren
```

What you can do instead is to drop the prefix/suffix and use
a small module as a namespace instead:

```ocaml
module Operator = struct
  type t = Plus | Minus | Times | Divide
end

module Hint = struct
  type t =
    | Name of name * type_args option
    | Array of tok
    | Question of tok * t
    | Tuple of hint_type comma_list paren
end
```

Now, at the use site you can select the most readable option depending
on the context. You can spell it all out if the variants are only used
briefly:

```ocaml
let operators = [Operator.Plus; Operator.Minus]
```

Or you can create a module alias if you use the variants a lot:

```ocaml
module Op = Operator

let operators = [Op.Plus; Op.Minus]
```

Or you can locally open the module if you need to use them
intensely in a particular scope:

```ocaml
let operators =
  let open Operator in
  [Plus; Minus; Times; Divide]

(* or *)

let operators =
  Operator.[Plus; Minus; Times; Divide]
```

Or you can just open the module at the top of
your file if that's your thing:

```ocaml
open Operators

let operators = [Plus; Minus; Times; Divide]
```

Modular Programming
-------------------

Now that you have a module like `Operator` you
suddenly realize that other definitions probably also
belong to it.

You might have functions with names such as `parse_operator` or
`action_of_operator`:

```ocaml
type operator = PlusOp | MinusOp | TimesOp | DivideOp

let parse_operator = function
  | "+" -> Some PlusOp
  | "-" -> Some MinusOp
  | "*" -> Some TimesOp
  | "/" -> Some DivideOp
  | _   -> None

let action_of_operator = function
  | PlusOp -> (+)
  | MinusOp -> (-)
  | TimesOp -> ( * )
  | Divide -> (/)
```

Now you can group them all in the namespace module
and give them more appropriate names (for module context):

```ocaml
module Operator = struct
  type t = Plus | Minus | Times | Divide

  let of_string = function
    | "+" -> Some Plus
    | "-" -> Some Minus
    | "*" -> Some Times
    | "/" -> Some Divide
    | _   -> None

  let to_action = function
    | Plus   -> (+)
    | Minus  -> (-)
    | Times  -> ( * )
    | Divide -> (/)
end
```

Namespacing functions this way has same benefits to
namespacing your original type. The new flexibility
affords you better readability or shorter expressions
at the call site.
For example, you can write something like this now:

```ocaml
let action =
  Operator.(source |> of_string |> to_action)
```

Another advantage is that such module
visually groups related type and functions in your source
file.

Yet another advantage: you can use your new
module in functor context, assuming it implements
the required signature:

```ocaml
module OperatorSet = Set.Make (Operator)
```

Conclusion
----------

One of my fist complains coming from object-oriented to
functional programming was that so much functional code
looks like big bags of functions and types with little
structure. Well, ML *structures* to the rescue!

Nowadays whenever I have a type and a bunch of related functions
(sounds familiar?),
I'm more inclined than not
to group them in a namespace module.
[☰](/ "Home")

## BibTeX

<small>
```       
@misc{Keleshev:2015-1,
  title="Namespacing Variants in ML",
  author="Vladimir Keleshev",
  year=2015,
  howpublished=
    "\url{https://keleshev.com/namespacing-variants-in-ml}",
}
```
</small>


<!--
<center markdown="1">
*Comment on [Reddit](http://www.reddit.com/r/ocaml/comments/32cxmw/namespacing_variants_in_ml/)*
<br/>
*Comment on [Hacker News](https://news.ycombinator.com/item?id=9364405)*
<br/>
*Follow me on [Twitter](http://twitter.com/keleshev)*
</center>
-->

* * *

*Did you like this blog post? If so, check out my new book:* Compiling to Assembly from Scratch. *It teaches you enough assembly programming and compiler fundamentals to implement a compiler for a small programming language.
*

