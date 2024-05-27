---
title: "Pretty Printing in OCaml: A Format Primer"
fancy-title: "Pretty Printing in OCaml<br/><small><small>A Format Primer</small></small>"
date: 2024-05-05
#cta: {book: false}
---

[Format](https://v2.ocaml.org/api/Format.html) is a module in OCaml standard library
that is used for writing pretty printers for code and data structures.
Projects like [ocamlformat](https://github.com/ocaml-ppx/ocamlformat) use it to implement very advanced code formatters.

Format has a very elegant and powerful core, but its interface is a bit clunky and unintuitive.
In this respect, it's a little bit like git: powerfull tool with a bit of antics, but very much worth learning.

But first, let's take a step back.

## `printf`

You're probably familliar with printf-style formatting.
It originated in C, but found its way into many modern languages.
Here are some example programs that print a string "Hello, 42 dolfins!" using printf-style formatting.

```c
/* C */
printf("Hello, %d %s!", 42, "dolfins");
```

```python
# Python
print("Hello, %d %s!" % (42, "dolfins"))
```

```javascript
// JavaScript
console.log("Hello, %d %s!", 42, "dolfins")
```

```ocaml
(* OCaml *)
printf "Hello, %d %s!" 42 "dolfins"
```

They consist of the *formatting string* `"Hello, %d %s!"` with two *format specifiers*, `%d` for an integer parameter, and `%s` for a string parameter.
Many more are available.

In OCaml, `printf` function is part of the
[Printf](https://v2.ocaml.org/api/Printf.html)
module.
It is made type safe by some interesting trickery which is outside of the scope for this article.
In short—*very much out-of-character for OCaml*—the string is coersed to another type: a GADT type `Stdlib.format`.

The Format module builds on top of that functionality and has its own version of `printf` function (and others).
Similar to the many %-style specifiers of Printf (like `%s` and `%d`), it adds many more @-style specifiers used to control the alignment and indentation (like `@[`, `@]` and `@;`).

It's best not to mix the two modules.
Printf is for casual printing to the console, Format—for data structures and code.

## `fprintf`

`fprintf`, which in C stands for "file print formatted", is a more general function that takes an additional parameter.
In C it takes a file descriptor; in OCaml `Printf.fprintf` takes an output channel.

In contrast, `Format.fprintf` takes something called "pretty print formatter", which is an abstraction.
It is usually shortened to `ppf`.
By selecting its implementation later, we can print to a file or a buffer or something more exotic and custom.

Let's start our journey by making sure we imported the `printf` and `fprintf` functions from the right module:

```ocaml
let printf = Format.printf
let fprintf = Format.fprintf
```

Let's write our first formatter function.
By convention they are either called `pp_<type>` or `<Module>.pp`, for example, `pp_json` or `JSON.pp`.
Let's start with something simple, a quoted string:

```ocaml
let pp_string ppf string =
  fprintf ppf "%S" string
```

The capital-S `%S` specifier produces a quoted string following the OCaml lexical conventions.

## `Format.pp_print_list`

Next function that we will "import" from the Format module is `pp_print_list`.
It takes a list of items to print, a pretty-printer for each item `pp_item`, and a separator `pp_sep`.

However, `pp_sep` needs to be a full-blown pretty-printer itself, which will be slightly too verbose for our needs, so we make a quick wrapper that allows to pass just the formatting string:

```ocaml
let pp_print_list ~sep pp_item =
  Format.pp_print_list
    ~pp_sep:(fun ppf () -> fprintf ppf sep) pp_item
```

* * *

> This `pp_print_list`… I guess it stands for "pretty print print list"?
> Well… long story short: Format predates the module system in OCaml (or Caml Light, should I say?).
> Back then when you loaded a module, you got all the functions in it, so it was a good practice to have a prefix for each function, like you do in C.
>
> Though, they did rename `list_length` to `List.length` at some point…


## Let Example

Now for our main example, we will be writing pretty printers for comma-separated lists with brackets for delimiters.
We will use this nested list to illustrate the different approaches:

```ocaml
let example = [
  [];
  ["one"; "two"; "three"];
  [
    "one"; "two"; "three"; "four"; "five";
    "six"; "seven"; "eight"; "nine"; "ten";
  ];
]
```

First, let's write a naïve implementation that is not very pretty and just prints the nested list in a single line:

```ocaml
let pp_list pp_item ppf list =
  fprintf ppf "[%a]"
    (pp_print_list ~sep:", " pp_item) list
```

We define `pp_list`—our main function.
It takes a `pp_item`, a pretty printer that knows how to print nested elements: sometimes they will be strings, other times—nested lists.
We define it using `fprintf` with a format `"[%a]"`.
This is similar to writing `"[%s]"`, but allows to pass a pretty printer with a value to print.
The value in this case is `list`, and the pretty printer—we construct it using `pp_print_list` which takes a separator and a printer for each item.

In fact, `pp_print_list` does all the heavy lifting here, while we only wrapped the result in brackets and specified comma (with a generous space) as the separator.

We can use `pp_list` to print the nested list `example` as follows:

```ocaml
printf "%a" (pp_list (pp_list pp_string)) example
```

As expected, the result is one long boring line:

```
[[], ["one", "two", "three"], ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]]
```

Let's add some indentation.

## Break hints

Just like regular `printf` strings have %-specifiers (`%s`, `%d`, etc.), Format uses @-specifiers for "boxes" and "break hints".

Break hints (or line-break–hints) allow us to tell the formatter: you may or may not break the line here.
They are written as `"@;"` and—importantly—take two integer parameters like this: `"@;<1 2>"`.

1. The first one is called "fits"—it specifies how many spaces (zero or more) should be printed if the expression fits on a single line.

2. The second one is called "breaks"—it specifies how many spaces of indentation should be used after the line break if the expression does not fit on a single line.

## Boxes

Boxes is another abstraction that goes hand-in-hand with break hints.

A box is "opened" with `"@["` and is "closed" with `"@]"`.
Opening a box takes a parameter that specifies the type of the box: `"@[<hv>"`.
We'll go through the various options further down.

Boxes and break hints work together as follows.
When you open a box, you say that the current column (where the box is introduced) is now the baseline for all indentation inside this box.
So when you later specify a break hint like `"@;<1 2>"` with "breaks" of two, and a break is necessary, the line will be broken and padded with spaces until it matches the column where the box is opened *plus* two spaces.

Nesting boxes allows nesting indentation levels.
The decision of fits-*vs*-breaks is made depending on the box type and the desired maximum *margin*.

```ocaml
let () = Format.set_margin 60
```

We set it 60 for the default `stdout` pretty print formatter used by printf, but this can be set per "ppf".

> The @-specifiers are hard to read at first, but eventually you get used to them just like with %-ones.
> We'll highlight them in strings for readability.

## Horizontal xor vertical "hv" box

The first type is "hv", written as `"@[<hv>…@]"`.
It is usually mentioned as "horizontal/vertical" box, but I like to call it "horizontal *xor* vertical" box to highlight the exclusive nature of the choice:

* If everything in the box fits on one line, it is layed out horizontally: every break hint becomes (zero or more) spaces, as specified by the first—"fits"—parameter.
* If everything does not fit on a single like, the layout is vertical: every break hint becomes a line break, followed by the baseline indentation of the box *plus* the second—"breaks"—parameter of spaces.

Let's reimplement `pp_list` using the newfound knowledge of boxes and break hints:

<!--
```ocaml
let pp_list pp_item ppf list =
  fprintf ppf "@[<hv>[%a]@]"
    (pp_print_list ~sep:",@;<1 1>" pp_item) list
```
-->

<style>
pre > i {
  /* background: #EEE; */
  /* border: 1px solid lightgrey; */
  border-radius: 7px;
  font-family:inherit;
  box-shadow: 0 0 0 1pt #DDD;
}
</style>

<pre><b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;hv&gt;</i>[%a]<i>@]</i>"❶
    (pp_print_list ~sep:",<i>@;&lt;1 1&gt;</i>"❷ pp_item) list
</pre>

<div class="circled-numbers">
1. We open an "hv" box before the opening bracket of the printed list, and close it after the closing bracket.

2. We specify the item separator as a literal comma, followed by a break hint: one space for "fits" and one for "breaks".
</div>

Run it through our `example`, and we get the following:

```
[[],
 ["one", "two", "three"],
 ["one",
  "two",
  "three",
  "four",
  "five",
  "six",
  "seven",
  "eight",
  "nine",
  "ten"]]
```

Not too bad! Let's unwrap.

The two shorter lists fit inside the 60 character margin, so they use comma plus one space for separators.

The longer list did not fit, so it used line breaks everywhere plus one space, *relative to the column just before the opening bracket*—where we opened our box.

If we want to put brackets on their own line, we add break hints:

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<hv>[@;<0 1>%a@;<0 0>]@]"
    (pp_print_list ~sep:",@;<1 1>" pp_item) list  -->

<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;hv&gt;</i>[<i>@;&lt;0 1&gt;</i>%a<i>@;&lt;0 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 1&gt;</i>" pp_item) list
</pre>

Same as before, but we put `@;<0 1>` just after the opening bracket and `@;<0 0>` just before the closing one.
Now the formatter has to break them as well if the items do not fit.

```
[
 [],
 ["one", "two", "three"],
 [
  "one",
  "two",
  "three",
  "four",
  "five",
  "six",
  "seven",
  "eight",
  "nine",
  "ten"
 ]
]
```

Both hints use zero for "fits" spaces, so no more whitespace is introduced for the compact lists.
For longer list the first break "breaks" to one space to make sure the first element is indented, and the last one breaks with zero spaces to make sure that the closing bracket is put back at the column "zero" relative to the opening bracket.

That was a minimal illustrative change, but one space indentation is a little bit odd.
Let's do two.

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<hv>[@;<0 2>%a@;<0 0>]@]"
    (pp_print_list ~sep:",@;<1 2>" pp_item) list
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;hv&gt;</i>[<i>@;&lt;0 2&gt;</i>%a<i>@;&lt;0 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 2&gt;</i>" pp_item) list
</pre>

```
[
  [],
  ["one", "two", "three"],
  [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten"
  ]
]
```

## Horizontal "h" box

Horizontal, or an "h" box ignores the "breaks" part of hints and lays out everything on a single line using the "fits" spaces:

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<h>[@;<0 2>%a@;<0 0>]@]"
    (pp_print_list ~sep:",@;<1 2>" pp_item) list
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;h&gt;</i>[<i>@;&lt;0 2&gt;</i>%a<i>@;&lt;0 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 2&gt;</i>" pp_item) list
</pre>

Just like our first naïve attempt did.

```
[[], ["one", "two", "three"], ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]]
```

## Vertical "v" box

Vertical "v" box is the opposite extreme: ignores the "fits" spaces and introduces breaks everywhere.

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<v>[@;<0 2>%a@;<0 0>]@]"
    (pp_print_list ~sep:",@;<1 2>" pp_item) list
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;v&gt;</i>[<i>@;&lt;0 2&gt;</i>%a<i>@;&lt;0 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 2&gt;</i>" pp_item) list
</pre>

Output:

```
[
  [

  ],
  [
    "one",
    "two",
    "three"
  ],
  [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten"
  ]
]
```

This is often the desirable layout, except for the ugly empty list.
For this case, I recommend pattern-matching on the empty list and printing it literally as `[]`.

## Compacting "hov" box

Compacting "hov" box is a fun one.
It tries to lay out as many items horisontally, but if they don't fit it only introduces a single break and continues horizontally.

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<hov>[@;<0 1>%a@;<0 0>]@]"
    (pp_print_list ~sep:",@;<1 1>" pp_item) list
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;hov&gt;</i>[<i>@;&lt;0 1&gt;</i>%a<i>@;&lt;0 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 1&gt;</i>" pp_item) list
</pre>

The result is very compact:

```
[[], ["one", "two", "three"],
 ["one", "two", "three", "four", "five", "six", "seven",
  "eight", "nine", "ten"]]
```

## Compacting "b" box

The "b" box is very similar to "hov", except for one detail…

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<b>[@;<0 1>%a@;<0 0>]@]"
    (pp_print_list ~sep:",@;<1 1>" pp_item) list
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;b&gt;</i>[<i>@;&lt;0 1&gt;</i>%a<i>@;&lt;0 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 1&gt;</i>" pp_item) list
</pre>

It always performs a break if a break reduces indentation.
The first break hint `@;<0 1>` and the following ones `@;<1 1>` have a "breaks" indent of one.
The last break hint `@;<0 0>` has indentation of zero, which is less then one, so the line is broken up.

```
[[], ["one", "two", "three"],
 ["one", "two", "three", "four", "five", "six", "seven",
  "eight", "nine", "ten"
 ]
]
```

I suppose that the "b" box is introduced specifically to support this kind of layout: closing delimiter on its own line.


## Comma-first

We are on a roll, let's add another example: a comma-first layout.

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<hv>[ %a@;<1 0>]@]"
    (pp_print_list ~sep:"@;<0 0>, " pp_item) list
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;hv&gt;</i>[ %a<i>@;&lt;1 0&gt;</i>]<i>@]</i>"
    (pp_print_list ~sep:"<i>@;&lt;0 0&gt;</i>, " pp_item) list
</pre>

We use an "hv" box, a break hint before the comma, and a break hint before the closing bracket.
As before, pattern-match on empty list to customize it.

```
[ [  ]
, [ "one", "two", "three" ]
, [ "one"
  , "two"
  , "three"
  , "four"
  , "five"
  , "six"
  , "seven"
  , "eight"
  , "nine"
  , "ten"
  ]
]
```

## Optional trailing comma

So far we have only wrangled with whitespace: spaces and newlines.
What if we want to introduce print characters when the layout fits or breaks?
A common requirement is to add a trailing comma in multi-line list definitions.

We can acheive it as follows:

<!--
let pp_list pp_item ppf list =
  fprintf ppf "@[<hv>[@;<0 2>%a%t]@]"
    (pp_print_list ~sep:",@;<1 2>" pp_item) list
    (Format.pp_print_custom_break
       ~fits:("", 0, "") ~breaks:(",", 0, ""))
-->
<pre>
<b>let</b> pp_list pp_item ppf list =
  fprintf ppf "<i>@[&lt;hv&gt;</i>[<i>@;&lt;0 2&gt;</i>%a%t]<i>@]</i>"
    (pp_print_list ~sep:",<i>@;&lt;1 2&gt;</i>" pp_item) list
    (Format.pp_print_custom_break
       ~fits:("", 0, "") ~breaks:(",", 0, ""))
</pre>

This example uses `pp_print_custom_break` and is a little bit more involved, so I refer you to the
[official documentation](https://ocaml.org/manual/5.1/api/Format.html#VALpp_print_custom_break)
for this one.

```
[
  [],
  ["one", "two", "three"],
  [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
  ],
]
```

Note the additional comma after `"ten"` and after the last nested list.

## Tips and tricks

* You can pass box and break hint parameters dynamically by using %-specifiers.
  For example: `"@[<%s>"` or `"@;<%d %d>"`.
* Negative parameters sometimes work, but are usually a hack: `"@;<0 -2>"`.
* `"@["` defaults to an `"@[<hv>"` box, but I prefer the full version for clarity.
* Boxes take a second parameter "indent", e.g. `"@[<hv 2>"`.
  It's like adding two to each nested hint's "breaks" parameter.
  I avoid this because it often leads to using negative break hints.
* `"@,"` is a shortcut for `"@;<0 0>"`; `"@ "`—for `"@;<1 0>"`.
  This is too much for me to remember.

Learn more in the official [Format documentation](https://ocaml.org/manual/5.1/api/Format.html).



<center><h2>Oh, btw, check out my book</h2></center>
<div style="text-align: center; line-height: 0px">
<a href="/compiling-to-assembly-from-scratch"
style="border-bottom: none; font-size: 0">
<img alt="Compiling to Assembly from Scratch, the book by Vladimir Keleshev"
src="/compiling-to-assembly-from-scratch.jpg"
style="box-shadow: rgb(0, 0, 0) 0px 0px 46px -23px"
width=200 height=300 />
</a>
</div>

## Bonus: JSON pretty-printer

As a treat, here's a complete and correct JSON pretty-printer.

```ocaml
module JSON = struct
  (* Invariants: utf8 strings, unique keys *)
  type t =
    | Null
    | Boolean of bool
    | Number of float
    | String of string
    | Array of t list
    | Object of (string * t) list

  (** Good-looking, round-trippable floats *)
  let number_to_string n =
    let s = sprintf "%.15g" n in
    if Float.of_string s = n then
      s
    else
      sprintf "%.17g" n

  let pp_string_body ppf =
    String.iter (function
      | '"'    -> fprintf ppf {|\"|} (* {|"|} *)
      | '\\'   -> fprintf ppf {|\\|}
      | '\b'   -> fprintf ppf {|\b|}
      | '\x0C' -> fprintf ppf {|\f|}
      | '\n'   -> fprintf ppf {|\n|}
      | '\r'   -> fprintf ppf {|\r|}
      | '\t'   -> fprintf ppf {|\t|}
      | '\x00'..'\x1F' as non_print_char ->
          fprintf ppf {|\u%.4X|} (Char.code non_print_char)
      | char   -> fprintf ppf {|%c|} char
    )

  let box pp ppf value = fprintf ppf "@[<hv>%a@]" pp value

  let rec pp ppf = function
    | Null      -> fprintf ppf "null"
    | Boolean b -> fprintf ppf "%b" b
    | Number n  -> fprintf ppf "%s" (number_to_string n)
    | String s  -> fprintf ppf {|"%a"|} pp_string_body s
    | Array a   -> fprintf ppf
       "[@;<0 2>%a@;<0 0>]"
       (pp_print_list ~sep:",@;<1 2>" (box pp)) a
    | Object o  -> fprintf ppf
       "{@;<0 2>%a@;<0 0>}"
       (pp_print_list ~sep:",@;<1 2>" (box pp_pair)) o

  and pp_pair ppf (field, value) =
    fprintf ppf {|"%a": %a|} pp_string_body field pp value

  let to_string = sprintf "%a" (box pp)
end
```


## [Source code](https://gist.github.com/keleshev/4322a18daa818a818f0ab49dfe3ed394)

<!--[☰](/ "Home") -->

## Citation

<small>
```
@misc{Keleshev:2024-1,
  title="Pretty Printing in OCaml: A Format Primer",
  author="Vladimir Keleshev",
  year=2024,
  howpublished=
    "\url{https://keleshev.com/pretty-printing-in-ocaml-a-format-primer}",
}
```
</small>


