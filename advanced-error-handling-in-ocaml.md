---
title: Advanced Error Handling in OCaml
fancy-title: "Advanced Error Handling<br/><small><small>in OCaml</small></small>"
subtitle: Multiple Errors, Error Recovery, Warnings
date: 2021-07-21
cta: {}
---

In a [previous blog post](/composable-error-handling-in-ocaml), we discussed using an OCaml feature called *polymorphic variants* for error handling.
Here, let's discuss some more advanced forms of this error-handling approach: returning multiple errors, performing error recovery, as well as handling warnings.

In many programs (for example, in a compiler or an IDE), we want to report all detected errors, instead of quitting on the first error.
We also often want to collect warnings that are not critical for the execution of the program.

To demonstrate the problem and the solutions, let's use an artificial example: a type checker for a small language with types `t` and terms `e`, which is technically a subset of OCaml:

<!--

t -> bool | int

e -> true | false
   | 0 | 1 | 2 | …
   | (e : t)
   | if e then e else e

-->

<p style="padding-left: 3.0em; text-indent: -1.25em" >
<em>&VeryThinSpace;t&nbsp;</em> → <b><code> bool </code></b>|<b><code> int</code><br/> </b>
</p>

<p style="padding-left: 3.0em; text-indent: -1.25em" >
<em>e&nbsp;</em> → <b><code> true </code></b>|<b><code> false</code><br/> </b>
  |<code> 0 </code>|<code> 1 </code>|<code> 2 </code>|<code> </code>…<br/>
  |<code> (</code><em>e</em><code> : </code><em>t</em><code>)</code><br/>
  |<b><code> if </code></b><em>e</em><b><code> then </code></b><em>e</em><b><code> else </code></b><em>e</em>
</p>

It's not a very useful language, but it is enough for us to discuss the interesting error handling cases.
We will represent this language with the following OCaml types:

```ocaml
module Type = struct
  type t = Bool | Int
end

module Term = struct
  type t =
    | Bool of bool
    | Int of int
    | Annotation of t * Type.t
    | If of {
        conditional: t; 
        consequence: t; 
        alternative: t;
      }
end

open Term
```

## Using exceptions

As a recap, let's first write the type checker while using exceptions for error handling.
We start by defining `failwithf`, which raises an exception like `failwith`, but allows printf-like formatting:

```ocaml
let failwithf f = Printf.ksprintf failwith f
```

And now, the type checker itself, in the form of a function called `infer`, which infers the type or fails with an exception:

```ocaml
let rec infer = function
  | Bool _ -> Type.Bool ❶
  | Int _ -> Type.Int
  | Annotation (term, annotated_t) -> ❷
      let term_t = infer term in
      if term_t <> annotated_t then
        failwithf "Expected %s, but got %s"
          (Type.to_string annotated_t) 
          (Type.to_string term_t)
      else
        annotated_t
  | If {conditional; consequence; alternative} -> ❸
      let conditional_t = infer conditional in
      let consequence_t = infer consequence in
      let alternative_t = infer alternative in
      if conditional_t <> Type.Bool then
        failwithf "If condition must be boolean"
      else if consequence_t <> alternative_t then
        failwithf "If branches must match: %s vs. %s"
          (Type.to_string consequence_t) 
          (Type.to_string alternative_t)
      else
        consequence_t
```

Writing type checkers, I find it helpful to follow a convention of adding an `_t` suffix to distinguish between terms and their types, like `term` and `term_t` above.
Some highlights:

<ol>
  <li style="padding-inline-start: 1ch; list-style-type: '❶'">
    For boolean and integer constants we can infer the type to be boolean or integer, respectively.
  </li>
  <li style="padding-inline-start: 1ch; list-style-type: '❷'">
    In case of a type annotation, we recursively infer the type (the process that can fail in itself) and compare it to the annotated type.
  </li>
  <li style="padding-inline-start: 1ch; list-style-type: '❸'">
    In case of an `if` conditional, we 
  </li>
  <ul>
    <li>
     infer the type of all terms,
    </li>
    <li>
      make sure that the conditional is boolean,
    </li>
    <li>
      make sure that the two branches have the same type.
    </li>
  </ul>
</ol>


## Polymorphic variants

Now, let's rewrite the type checker using the result type with polymorphic variants for errors (like we did in the earlier blog post):

```ocaml
let return x = Ok x
let error x = Error x
let (let*) = Result.bind

let rec infer = function
  | Bool _ -> return Type.Bool
  | Int _ -> return Type.Int
  | Annotation (term, annotated_t) ->
      let* term_t = infer term in
      if term_t <> annotated_t then
        error (`Expected_x_got_y (annotated_t, term_t))
      else
        return annotated_t
  | If {conditional; consequence; alternative} ->
      let* conditional_t = infer conditional in
      let* consequence_t = infer consequence in
      let* alternative_t = infer alternative in
      if conditional_t <> Type.Bool then
        error `If_conditional_must_be_boolean
      else if consequence_t <> alternative_t then
        error (`If_branches_must_match (consequence_t,
                                        alternative_t))
      else
        return consequence_t
```

It reads very similarly.
We have used `Result.bind` for our `let*` bindings instead of the regular `let` bindings.
We also used `return` and `error` as aliases for `Ok` and `Error` result constructors.

Instead of raising an exception, the `infer` function returns a type `(Type.t, _) result` where `_` is the inferred polymorphic variant type.
Still, our type checker stops at the first error.
Let's change that.

## Handling multiple errors

As the first step, let's change our `error` alias to allow for a list of errors to be returned:

```ocaml
let error x = Error [x]
```

This changes the return type of `infer` to `(Type.t, _ list) result`.

Now, to actually return multiple errors we need to control which bindings are short-circuiting as before and which bindings can be used to detect and report errors together.
For example, we can't report that the *conditional must be boolean* before we infer the type of the conditional, but we can report errors happening in both conditional branches (the consequence and the alternative) as they can be checked separately.
Fortunately, OCaml has a neat feature to help us with that.

Similarly to how consequent `let` bindings are dependent on each other, `and` bindings allow to bind independent values.
And OCaml allows custom `and*` bindings similarly to custom `let*` bindings.

> The `and*` bindings are syntactic sugar for monoidal products.
> For more info, see the [relevant section of the OCaml Manual](https://ocaml.org/manual/bindingops.html).


We can specify that when two bindings are combined using `and*` the error lists are appended, using the `@` operator below:

```ocaml
let (and*) left right = match left, right with
  | Ok left, Ok right -> Ok (left, right)
  | Error left, Error right -> Error (left @ right)
  | Error e, _ | _, Error e -> Error e
```

> Appending lists is not efficient, so a different data structure would be a better fit here, such as a *catenation list*.
> But that's a topic for a different blog post.

Now, for cases where errors can be detected independently we can use the `and*` bindings.
We need some care to apply them in the right places to catch as many independent errors as possible.
As a result, our type checker now looks like this:

```ocaml
let return x = Ok x
let error x = Error [x]
let (let*) = Result.bind

let (and*) left right = match left, right with
  | Ok left, Ok right -> Ok (left, right)
  | Error left, Error right -> Error (left @ right)
  | Error e, _ | _, Error e -> Error e

let rec infer = function
  | Bool _ -> return Type.Bool
  | Int _ -> return Type.Int
  | Annotation (term, annotated_t) ->
      let* term_t = infer term in
      if term_t <> annotated_t then
        error (`Expected_x_got_y (annotated_t, term_t))
      else
        return annotated_t
  | If {conditional; consequence; alternative} ->
      let* () =
        let* conditional_t = infer conditional in
        if conditional_t <> Type.Bool then
          error `If_conditional_must_be_boolean
        else
          return ()
      and* result_t =
        let* consequence_t = infer consequence
        and* alternative_t = infer alternative in
        if consequence_t <> alternative_t then
          error (`If_branches_must_match (consequence_t, 
                                          alternative_t))
        else
          return consequence_t
      in
      return result_t
```

The error handling is a bit more involved than before, but it can capture many possible errors.
For example, type checking the following program…

```ocaml
if 1 then 2 else true
```

…will detect both the non-boolean conditional and the branch mismatch errors:


```ocaml
assert (infer (If {
  conditional=Int 1;
  consequence=Int 2;
  alternative=Bool true;
}) = Error [
  `If_conditional_must_be_boolean;
  `If_branches_must_match (Type.Int, Type.Bool);
]);
```

While checking the following snippet…

```ocaml
if (1: bool) then (2: bool) else (true: int)
```

…our type-checker will capture all three annotation errors (unlike what the OCaml compiler does, for example):

```ocaml
assert (infer (If {               
  conditional=Annotation (Int 1, Type.Bool);
  consequence=Annotation (Int 2, Type.Bool);
  alternative=Annotation (Bool true, Type.Int);
}) = Error [
  `Expected_x_got_y (Type.Bool, Type.Int);
  `Expected_x_got_y (Type.Bool, Type.Int);
  `Expected_x_got_y (Type.Int, Type.Bool);
]);
```

> We should include the source code locations with the errors in practice to point to the right place in the source code.

Even though we find and report multiple errors, we have not considered the possibility of error recovery.
For example, in case of an annotation we could detect and report a type mismatch, but then recover by assuming that the annotation is correct to continue type checking (and potentially uncover more errors).
To achieve that, we need to change our approach slightly.

## Error recovery

The `result` type can express either a success result on an error (or a list of errors, in our case).
To express a result obtained after recovering from an error, we need to change the `result` type from a variant type to a sum type.
For a lack of a better name, let's call such type an `outcome`:

```ocaml
type ('ok, 'error) outcome = {
  result: 'ok option;
  errors: 'error list;
}
```

Let's reimplement `return`, `error`, `(let*)`, and `(and*)` for this type:

```ocaml
let return x = {result=Some x; errors=[]}
let error x = {result=None; errors=[x]}

let (let*) body callback = match body with
  | {result=None; errors} as e -> e
  | {result=Some ok; errors=previous_errors} ->
      let {result; errors} = callback ok in
      {result; errors=previous_errors @ errors}

let (and*) left right =
  let result = match left.result, right.result with
    | Some left, Some right -> Some (left, right)
    | _ -> None
  in
  {result; errors=left.errors @ right.errors}
```

The implementation is very similar as before, including `(let*)`, which has some similarities to how `Result.bind` is implemented.

With these combinators, our existing type checker works the same way without change.
The only difference is in the shape of the return type.
So far, this gives us nothing. 
That is, until we add a new combinator function:

```ocaml
let recoverable_error x = {result=Some (); errors=[x]}
```

It is a constructor that holds a non-empty result *and* an error.
This allows us to capture the error and recover from it by returning a result.

Now we can change how we handle annotations:

```ocaml
let rec infer = function
  | Bool _ -> return Type.Bool
  | Int _ -> return Type.Int
  | Annotation (term, annotated_t) ->
      let* term_t = infer term in
      let* () =
        if term_t <> annotated_t then
          recoverable_error (
            `Expected_x_got_y (annotated_t, term_t))
        else
          return ()
      in
      return annotated_t
  | If {conditional; consequence; alternative} ->
      …
```

Here, if the annotated and the inferred types do not match, we report a recoverable error but continue by returning the annotated type.

This affects our previous example:

```ocaml
if (1: bool) then (2: bool) else (true: int)
```

This will capture an additional error: the fact that the two branches are of a different type.

```ocaml
assert (infer (If {
  conditional=Annotation (Int 1, Type.Bool);
  consequence=Annotation (Int 2, Type.Bool);
  alternative=Annotation (Bool true, Type.Int);
}) = {
  result=None;
  errors=[
    `Expected_x_got_y (Type.Bool, Type.Int);
    `Expected_x_got_y (Type.Bool, Type.Int);
    `Expected_x_got_y (Type.Int, Type.Bool);
    `If_branches_must_match (Type.Bool, Type.Int);
  ];
});
```

So, thanks to error recovery, we can capture more errors.

> What we have implemented can be described as a composition of an option monad and a writer monad.
> Similar results can be achieved using a monad transformer library.

## Warnings

Since OCaml is not a purely functional language, we can just print warning messages to the `stderr` channel, as they happen, without anything special.
For that, we can use `eprintf` from the `Printf` module, or we can use a logging library.
We can also append warnings to a mutable collection to deal with them later.

To handle warnings, a logical extension of our purely-functional approach would be to add a `warnings` record field to the outcome type:

```ocaml
type ('ok, 'error, 'warning) t = {
  result: 'ok option;
  errors: 'error list;
  warnings: 'warning list;
}
```

And a combinator that introduces warnings:

```ocaml
let warn w = {result=Some (); errors=[]; warnings=[w]}
```

This way, we can, for example, issue a warning in case an `if` conditional is a constant:

```ocaml
   let* () = 
     let* conditional_t = infer conditional in
       if conditional_t <> Type.Bool then
         error `If_conditional_must_be_boolean
       else
         match conditional with
         | Bool value ->
             warn (`Conditional_always value)
         | _ ->
             return ()
```

Now, let's go and write some friendly programs that help presenting a comprehensive view of errors and warnings to the user, instead of bailing out at first sight of a problem.
[☰](/ "Home")

## Newsletter

> Subscribe to receive an occasional email from me about compilers, functional programming, or my book [Compiling to Assembly from Scratch](/compiling-to-assembly-from-scratch).
>
> <script async data-uid="8529ea38b4" src="https://motivated-writer-7421.ck.page/8529ea38b4/index.js"></script>
>
> Unsibscribe at any time.
>

## References

* All code from this blog post in a runnable [gist](https://gist.github.com/keleshev/a153fa3ce9e3e341baa25d2b7cff6bac)
* The OCaml Manual on [binding operators](https://ocaml.org/manual/bindingops.html)

## BibTeX

<small>
```
@misc{Keleshev:2021-1,
  title="Advanced Error Handling in OCaml",
  author="Vladimir Keleshev",
  year=2021,
  howpublished=
    "\url{https://keleshev.com/advanced-error-handling-in-ocaml}",
}
```
</small>


<!-- * * * -->

<!--
*Did you like this blog post? Cool! But did you know I wrote a whole book! It's called* Compiling to Assembly from Scratch. *It teaches you enough assembly programming and compiler fundamentals to implement a compiler for a small programming language. From scratch. Check it out:*
-->
