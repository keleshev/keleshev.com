

Point-free Pattern Matching
==================================

<center>2018-12-18</center>

Sometimes you've got a simple variant type, like this one:


```ocaml
module Zero_one_many = struct
  type t =
    | Zero
    | One of string
    | Many of string list
end
```

So you start writing some basic functions for it, like the following ones.
Sometimes many of them.


```ocaml
let to_string = function
  | Zero -> &quot;(zero)&quot;
  | One s -> s
  | Many list -> String.concat &quot;, &quot; list

let count = function
  | Zero -> 0
  | One _ -> 1
  | Many list -> List.length list
```

And it feels like a lot of code that is not saying much.
That's because pattern matching has this rigid syntactical structure.
An alternative is to write a function for case
analysis that uses labeled parameters, instead of pattern matching:


```ocaml
let case ~zero ~one ~many = function
  | Zero -> zero
  | One s -> one s
  | Many list -> many list
```

Now we can express the same functions more concisely, primarily
because we can use the point-free style:


```ocaml
let to_string =
  case ~zero:&quot;(zero)&quot; ~one&colon;id ~many:(String.concat &quot;, &quot;)

let count =
  case ~zero&colon;0 ~one:(const 1) ~many&colon;List.length
```

<p><center>&#8258;</center></p>

Compare, there is a symmetry between pattern matching and this style
of case analysis using labeled parameters:

### Pattern matching:

```ocaml
let to_string = function
  | Zero -> &quot;(zero)&quot;
  | One s -> s
  | Many list -> String.concat &quot;, &quot; list
```

### Point-full functional case analysis:

```ocaml
let to_string =
  case
    ~zero&colon;&quot;(zero)&quot;
    ~one:(fun s -> s)
    ~many:(fun list -> String.concat &quot;, &quot; list)
```

### Point-free functional case analysis:

```ocaml
let to_string =
  case ~zero:&quot;(zero)&quot; ~one&colon;id ~many:(String.concat &quot;, &quot;)
```

The difference is that for functions we can perform
[η-conversion](https://en.wikipedia.org/wiki/Lambda_calculus#η-conversion)
to make
the definition more concise, and in many—*but not all!*—cases, more readable.


## Is this just fold?

As you might have noticed the *case* function is similar to
*[fold](./interpretations-of-fold)*.
Except *fold* does both case analysis and is a recursion scheme,
while *case* does only case analysis.
For non-recursive data types, *case* and *fold* are the same function.


## Case for Abstract Types

There is a different use-case for *case*:
to expose a pattern-matching-like facility for abstract types.
For example, we can re-define our original `Zero_one_many.t`
type as an abstract type with a different implementation:

```ocaml
module Zero_one_many : sig
  type t

  val case : zero:'a
          -> one:(string -> 'a)
          -> many:(string list -> 'a)
          -> t
          -> 'a

  val to_string : t -> string
end = struct
  type t = string list

  let case ~zero ~one ~many = function
    | [] -> zero
    | [s] -> one s
    | list -> many list

  let to_string =
    case ~zero:&quot;(zero)&quot; ~one&colon;id ~many:(String.concat &quot;, &quot;)
end
```

We implemented the type as a `string list`, but we could have used
our original variant implementation. And that's the beauty of it.
We can go back and forth between implementations without
breaking the interface, while still delivering a decent
tool for case analysis.

## Case for Concrete Types

Yet another use-case for *case* is to provide new
ways of case analysis for existing concrete types.
For example, we can do a case analysis on `int` to
decide if it is even or odd:

```ocaml
module Parity = struct
  let case ~even ~odd n =
    if n mod 2 = 0 then even n else odd n
end

module Test = struct
  open Printf

  Parity.case 42
    ~even:(fun n -> printf &quot;%d is even\n&quot; n)
    ~odd:(fun n -> printf &quot;%d is odd\n&quot; n);

  Parity.case 42
    ~even:(printf &quot;%d is even\n&quot;)
    ~odd:(printf &quot;%d is odd\n&quot;);
end
```

## Code

The code is available in a [GitHub gist][gist].

[gist]: https://gist.github.com/keleshev/a7e28bb2163e2a88da60d44d03169b2d

## Conclusion

The *case* function is a small and sometimes useful pattern
that can simplify some code.
If you haven't yet learned about its more powerfull
cousin *fold* then read my
*[Interpretations of Fold](./interpretations-of-fold)*. [&#9632;](/ "Home")







<p><center>&#8258;</center></p>

<center markdown="1">
<em>Follow me on <a href="http://twitter.com/keleshev">Twitter</a></em>
</center>








