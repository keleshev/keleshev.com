---
title: Composable Error Handling in OCaml
fancy-title: "Composable Error Handling<br/><small><small>in OCaml</small></small>"
date: 2018-02-12
cta: {book: yes}
---

Let's discuss common ways to handle errors in OCaml, their shortcomings,
and finally, how polymorphic variants may help. The discussion applies
equally well to [Reason ML][Reason].

[Reason]: https://reasonml.github.io/

If you need an introduction to the topic, I recommend
Real World OCaml chapter on [Error Handling][RWO-ER].

[RWO-ER]: https://realworldocaml.org/v1/en/html/error-handling.html

As a reference point, we'll take three hypothetical functions which can return
errors and which we want to compose:

 * `Parser.parse`, which can yield a "syntax error" or a "grammar error".
 * `Validation.perform`, which can yield a "length error" or a "height error".
 * `Display.render`, which can yield a "display error".

We will cover the following error-handling approaches:

<ol type="A">
  <li>Exceptions for errors</li>
  <li>Result type with strings for errors</i>
  <li>Result type with custom variants for errors</i>
  <li>Result type with polymorphic variants for errors</i>
</ol>

## A. Exceptions for errors

First, let us consider a version of our interface where the above functions
use exceptions to signal errors.

```ocaml
type tree

module Parser : sig
  exception SyntaxError of int
  exception GrammarError of {line: int; message: string}

  (** Can raise [Parser.SyntaxError]
      or [Parser.GrammarError] *)
  val parse : string -> tree
end

module Validation : sig
  exception LengthError of int
  exception HeightError of int

  (** Can raise [Validation.LengthError]
      or [Validation.HeightError] *)
  val perform : tree -> tree
end

module Display : sig
  exception Error of string

  (** Can raise [Display.Error] *)
  val render : tree -> string
end
```

Here is how we can write code that composes these functions while ignoring the errors:

```ocaml
let main source =
  let tree = Parser.parse source in
  let tree = Validation.perform tree in
  Display.render tree
```

And here is how we can write code that handles and reports each error:

```ocaml
open Printf

let handle_errors source =
  try
    printf "%s" (main source)
  with
    | Parser.SyntaxError line ->
        eprintf "Syntax error at line %d" line
    | Parser.(GrammarError {line; message}) ->
        eprintf "Grammar error at line %d: %s" line message
    | Validation.LengthError length ->
        eprintf "Validation error: ";
        eprintf "length %d is out of bounds" length
    | Validation.HeightError height ->
        eprintf "Validation error: ";
        eprintf "height %d is out of bounds" height
    | Display.Error message ->
        eprintf "Display error: %s" message
```

*Upsides:*

 * **Composition**. Functions compose freely.
 * **Concern separation**. Happy path and error handling are separated.
 * **Distinguishable errors**. We can reliably distinguish one kind of
   error from another–for example, a `SyntaxError` from a `GrammarError`.
 * Also, in OCaml, the exception mechanism is fast and fits well
   with performance-critical sections of code.

*Downsides:*

 * No **error contract**.
   Comment on a function signature is our only hope to know
   that a function can raise as well as which exact exceptions it can raise.
   Nothing can save us from a comment that is missing, incorrect, or out-of-date.
   We could use a popular naming convention and name
   our function `Parser.parse_exn`. This is definitely worthwhile, but
   similar shortcomings apply.
 * No **exhaustiveness checking**. We cannot be sure that we handled all the
   error cases at a relevant call site
   or that the cases we are covering are relevant at all.
   If we change one of the called functions to return a new kind of
   error, then the compiler will not inform us about the call sites that are
   affected.

Although the flaws of the exception-based approach are real and dire,
it is important to recognize the upsides to adequately compare
this approach with the other.


## B. Result type with strings for errors

The OCaml built-in `Stdlib.result` type provides a reusable way to express
and distinguish a success value and an error value.

```ocaml
type ('success, 'error) result =
  | Ok of 'success
  | Error of 'error
```

Since version 4.08, OCaml contains a `Result` module that contains helper functions to operate on the result type.

One way to use the result type is to use a string for the `'error` parameter, that describes the error textually.
This way, our interface will look like this:

```ocaml
module Parser : sig
  val parse : string -> (tree, string) result
end

module Validation : sig
  val perform : tree -> (tree, string) result
end

module Display : sig
  val render : tree -> (string, string) result
end
```

We could handle errors by manually matching on the result type:

```ocaml
let main source =
  match Parser.parse source with
  | Error message ->
      eprintf "Parser error: %s" message
  | Ok tree ->
      match Validation.perform tree with
      | Error message ->
          eprintf "Validation error: %s" message
      | Ok tree ->
          match Display.render tree with
          | Error message ->
              eprintf "Display error: %s" message
          | Ok output ->
              printf "%s" output
```

Or we could use `Result.bind` to monadically compose the result-returning functions and thus separate error handling from the happy path.

```ocaml
let main source =
  Result.bind (Parser.parse source) (fun tree ->
    Result.bind (Validation.perform tree) (fun tree ->
      Display.render tree))
```

However, it is more common to use an infix operator `(>>=)` for `bind`:

```ocaml
let (>>=) = Result.bind

let main source =
  Parser.parse source >>= fun tree ->
  Validation.perform tree >>= fun tree ->
  Display.render tree
```

Since OCaml 4.08 you can also use binding operators:

```ocaml
let (let*) = Result.bind

let main source =
  let* tree = Parse.parse source in
  let* tree = Validation.perform tree in
  Display.render tree
```

Notice how similar this looks to our original version based on exceptions:

```ocaml
let main source =
  let tree = Parser.parse source in
  let tree = Validation.perform tree in
  Display.render tree
```

In both cases we can handle the errors separately from the happy path:

```ocaml
let handle_errors source =
  match main source with
  | Error message -> eprintf "Error: %s" message
  | Ok output -> printf "%s" output
```


*Upsides:*

 * **Composition**. Functions compose using the result monad.
 * **Concern separation**. The error handling and the happy-path code can be separated.
 * **_Weak_ error contract**. The fact that a function can return an error is
   part of the type signature. However, we can't infer which exact errors are
   part of the contract.

*Downsides:*

 * Non-**distinguishable errors**. At the site where we handle errors we can't
   distinguish two errors, for example, a "length error" from a "height error".
 * No **exhaustiveness checking**. When a new error case is introduced, the
   compiler will not help us find the call sites where a change would be relevant.

Compared with _A. Exceptions for errors_ approach, we lose the ability to distinguish
errors, maintain the ability to compose functions, and gain the ability
to know from a type signature that a function can return an error.

## C. Result type with custom variants for errors

A natural way to improve upon the previous example would be to use the result type
with a custom variant type for the `'error` type parameter instead of string:

```ocaml
module Parser : sig
  type error =
    | SyntaxError of int
    | GrammarError of {line: int; message: string}

  val parse : string -> (tree, error) result
end

module Validation : sig
  type error =
    | LengthError of int
    | HeightError of int

  val perform : tree -> (tree, error) result
end

module Display : sig
  val render : tree -> (string, string) result
end
```

We can handle errors by manually matching on the result type:

```ocaml
let main source =
  match Parser.parse source with
  | Error Parser.(SyntaxError line) ->
      eprintf "Syntax error at line %d" line
  | Error Parser.(GrammarError {line; message}) ->
      eprintf "Grammar error at line %d: %s" line message
  | Ok tree ->
      match Validation.perform tree with
      | Error Parser.(LengthError length) ->
          eprintf "Validation error: ";
          eprintf "length %d is out of bounds" length
      | Error Parser.(HeightError height) ->
          eprintf "Validation error: ";
          eprintf "height %d is out of bounds" height
      | Ok tree ->
          match Display.render tree with
          | Error message ->
              eprintf "Display error: %s" message
          | Ok output ->
              printf "%s" output
```

However, if we try to compose the three functions monadically (like we
did in the previous example), we discover that it is not possible
because the bind operator requires the `'error` type parameters of different
functions to unify (notably, unlike the `'success` type parameter):

```ocaml
val (bind) : ('a, 'error) result
          -> ('a -> ('b, 'error) result)
          -> ('b, 'error) result
```

*Upsides:*

 * **Error contract**. The type—not a comment—reflects the relevant error cases.
 * **Distinguishable errors**. We can pattern-match to distinguish errors.
 * **Exhaustiveness checking**. When the called function gets an additional error case,
   the compiler will show all the call sites that need to be updated.

*Downsides:*

 * No **composition**. We can't compose the functions directly, monadically, or otherwise.
 * No **concern separation**. We are forced to deal with
   the error branch using pattern matching or combinators.

There is a way to work around the two downsides. You can lift each function
you want to compose to a result type where `'error` can encompass all the
possible errors in your combined expression.
However, that adds boilerplate per each function and requires
to manage the new "large" error type.

Compared with _B. Result type with strings for errors_ approach, we lose
composition (wich is a big deal), mix up the happy path with error handling,
but regain the ability to distinguish and exhaustively check error cases,
while having a strong error contract.

Seems like you can't have the cake and eat it too.
This is also usually the point where best practices of other
statically-typed functional languages stop, and you have to deal with the
trade-offs.

## D. Result type with polymorphic variants for errors

Polymorphic variants allow you to have the cake and eat it too. Here's how.

Let's port our previous example to use polymorphic variants instead of the
nominal variants.

```ocaml
module Parser : sig
  type error = [
    | `ParserSyntaxError of int
    | `ParserGrammarError of int * string
  ]

  val parse : string -> (tree, [> error]) result
end

module Validation : sig
  type error = [
    | `ValidationLengthError of int
    | `ValidationHeightError of int
  ]

  val perform : tree -> (tree, [> error]) result
end

module Display : sig
  type error = [
    | `DisplayError of string
  ]

  val render : tree -> (string, [> error]) result
end
```

The key feature of polymorphic variants is that
they unify with other polymorphic variants.
We specifically annotated
our functions with `[> error]` to signify that this
error type can unify with "larger" polymorphic variants.

> *There’s more to polymorphic variants, but it’s outside of scope for this
> article. You will find links to resources about polymorphic variants below.*

Now look, if you compose just two functions, parser and validator:

```ocaml
let parse_and_validate source =
  let* tree = Parser.parse source in
  Validation.perform tree
```

Then not only will this work, but the type of such a function will be as follows:

```ocaml
val parse_and_validate : string -> (tree, [>
  | `ParserSyntaxError of int
  | `ParserGrammarError of int * string
  | `ValidationLengthError of int
  | `ValidationHeightError of int
]) result
```

As you can see, the error branch of the result type is a union of the two
variants of the parser errors *and* the two variants of the validator errors!

Let us now throw in our render function:

```ocaml
let main source =
  let* tree = Parser.parse source in
  let* tree = Validation.perform tree in
  Display.render tree
```

The inferred function type will reflect all the relevant error cases:

```ocaml
val main : string -> (string, [>
  | `ParserSyntaxError of int
  | `ParserGrammarError of int * string
  | `ValidationLengthError of int
  | `ValidationHeightError of int
  | `DisplayError of string
]) result
```

This way, if your error-returning functions use polymorphic variants for
error branches, then you can compose as many of them as you want and the
resulting type that will be infered will reflect the exact error cases
that the composed function can exibit.

You handle the errors by pattern matching on the result type:

```ocaml
let handle_errors source =
  match main source with
  | Ok output ->
      printf "%s" output
  | Error (`ParserSyntaxError line) ->
      eprintf "Syntax error at line %d" line
  | Error (`ParserGrammarError (line, message)) ->
      eprintf "Grammar error at line %d: %s" line message
  | Error (`ValidationLengthError length) ->
      eprintf "Validation error: ";
      eprintf "length %d is out of bounds" length
  | Error (`ValidationHeightError height) ->
      eprintf "Validation error: ";
      eprintf "height %d is out of bounds" height
  | Error (`DisplayError message) ->
      eprintf "Display error: %s" message
```

*Summary:*

 * **Composition**. Functions compose monadically by unifying the `'error`
   branch of the result type.
 * **Concern separation**. Happy path and error handling can be separated.
 * **Error contract**. Polymorphic variant type reflects the relevant error cases.
 * **Distinguishable errors**. We can pattern-match to distinguish errors.
 * **Exhaustiveness checking**. When the called function gets an additional error case,
   the compiler will show all the call sites that need to be updated.

There are no downsides to this approach that I can think of. However, it is
worth noting that the names of each polymorphic variant should be globally
distinguishable. So you need a descriptive name, for example,
<code>&#96;MyModuleNameErrorName</code>
as opposed to <code>&#96;ErrorName</code>.



## Conclusion

Polymorphic variants in OCaml have many use cases. But just this one use case
makes the language stand out from the others.
I often miss higher-kinded types or type classes.
Still, I have hard time imagining my daily work without being able to handle error this way:
composing error-returning functions effortlessly and with full type safety.

I would like to encourage library authors (including standard library authors)
to use this error-handling approach as the default one, so we can take
error-returning functions from different libraries and compose them freely.

In a follow-up article I will discuss this approach futher and introduce a few useful patterns around it.

## Resources

This approach to error handling scales well. However, it requires good
familiarity with how polymorphic variants work. Here are a few resources:

* Chapter of Real World OCaml on [Polymorhic Variants][RWO-POLY]
* Axel Rauschmayer's [ReasonML: polymorphic variant types][Axel],
  which has a further list of valuable resources

[RWO-POLY]: https://realworldocaml.org/v1/en/html/variants.html#polymorphic-variants
[Axel]: http://2ality.com/2018/01/polymorphic-variants-reasonml.html

## [Code](https://gist.github.com/keleshev/c8d6d8adac646839fdc6664d44cb91c6)

<!--Code from this article is available in a [gist](https://gist.github.com/keleshev/c8d6d8adac646839fdc6664d44cb91c6).-->

## Update

* 2020-12-08: The article was updated to use the new
  [`Stdlib.Result`](stdlib-result) module and `let*` syntax.
  Previously it used
  [`Base.Result`](base-result) and [`ppx_let`](ppx_let).

## Acknowledgments

Big thanks to [Oskar Wickström](https://twitter.com/owickstrom)
for giving feedback on a draft of this post. [&#9632;](/ "Home")


[base-result]: https://ocaml.janestreet.com/ocaml-core/latest/doc/base/Base/Result/index.html
[ppx_let]: https://github.com/janestreet/ppx_let
[stdlib-result]: https://caml.inria.fr/pub/docs/manual-ocaml/libref/Result.html

* * *

*Did you like this blog post? If so, check out my new book:* Compiling to Assembly from Scratch. *It teaches you enough assembly programming and compiler fundamentals to implement a compiler for a small programming language.
*


