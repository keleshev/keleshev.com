---
title: Parsing Ambiguity: Type Argument v. Less Than — Vladimir Keleshev
---


<style> #home { position:absolute; line-height: inherit; } </style>

<span id=home><a title=Home href=/>☰</a></span>

<h1>
Parsing Ambiguity:<br/>Type Argument <em>v.</em> Less Than</h1>

<center>2016-06-19</center>

In C-family languages, type arguments are usually
delimited with "angular" brackets, like this:

```txt
Array&lt;String&gt;
```

In an expression context, the angular brackets could be
confused with infix comparison operators.
Think about the difference between the following two expressions:

```txt
x = Foo&lt;Bar&gt;(1 + 2)

x = foo &lt; bar &gt; (1 + 2)
```

How should the parser determine that the first one
is a constructor call, and the second one is
two infix comparisons?

This problem can be solved on different levels:

* lexer level,
* parser level, or
* language design level.

First, let's start with lexer-level solutions.

## The lexer hack

We can make lexer keep track of type names.
Every time
we encounter a definition like `class Foo`,
we add the type name to a symbol table.
Next, when the lexer encounters an identifier,
we check if this identifier is present in that symbol table.
If it is present in the symbol table,
we issue a `TYPE_IDENTIFIER` token, otherwise an `IDENTIFIER` token.

This removes the ambiguity for the parser since
`TYPE_IDENTIFIER '<'` is clearly the start of a type expression,
while `IDENTIFIER '<'` is a start of a comparison.

This solution is called
[the lexer hack](https://en.wikipedia.org/wiki/The_lexer_hack).
It was first used in C.

There are several problems with this solution:

* If your language allows forward references, then you
  need two separate passes: the first pass to construct the
  symbol table, and the second pass that issues the tokens.

* Depending on how complex your type declaration
syntax is, you might need to do some actual parsing in your
tokenizer to extract the identifier of your type.

For example, in C, type declarations can get quite complicated.
Here is some standards-compliant code that shows this:

```c
typedef int (*foo)(int bar, int, baz);
```

Of *all* the identifiers here, it is not trivial to
determine that "`foo`" is the type being introduced.
Especially during lexing.
For this, you have to do some parsing in your lexer.

## Lexer whitespace sensitivity

Depending on whitespace surrounding "`<`" and "`>`" symbols,
the lexer can issue different tokens.
For example, if the next token matches a `"<\s"` regular
expression—issue `LESS_THAN` token.
Otherwise, if it matches just `"<"`—issue `LEFT_ANGLE_BRACKET`.

The reality might be more complicated (or not).
You need to consider cases like this:

```txt
Array&lt;/* hello! */String&gt;
```

One language that takes this approach is Swift.
[Swift uses whitespace](https://developer.apple.com/library/ios/documentation/Swift/Conceptual/Swift_Programming_Language/LexicalStructure.html#//apple_ref/doc/uid/TP40014097-CH30-ID418)
to assign meaning to operator tokens.

This solution can be considered a language-level
since it affects the set and meaning of accepted programs.
This solution is also well applicable to lexer-less
parsing techniques, like PEG and classical parser combinators.

<center>⁂</center>

Now we move onto parser-level solutions.

## Prioritized choice (PEG)

[Parsing expression grammars](
https://pdos.csail.mit.edu/papers/parsing:popl04.pdf)
(PEG) have an interesting feature,
the *prioritized choice* operator "`/`" *(forward slash)*.
Unlike the regular *choice* operator
"`|`" *(vertical bar)*, it
allows one grammar rule to be prioritized over another.

For example, it allows you to say that
we first consider "`<`" to start
a type argument list, and if this interpretation fails
to parse, we backtrack and try to interpret it as an
infix comparison.
Here's how a simplified PEG grammar like that can look like:

```python2
constructor_call &lt;-
  identifier '&lt;' type_parameters '&gt;' '(' parameters ')'

infix_expression <-
  identifier (('&lt;' / '&gt;') identifier)*

expression <-
  # `constructor_call` takes priority if ambiguity arises:
  constructor_call / infix_expression / '(' expression ')'
```

## Generalized parsing

If PEG allows you to make a choice between two production rules,
[generalized parsers like GLR](https://en.wikipedia.org/wiki/GLR_parser)
allow you to defer the choice until after parsing.
In the case of syntactic ambiguity,
a GLR parser will produce two parse trees:
one for type expression, another for infix expression.
At a later stage of compilation
(for example, when you construct your symbol tables)
you can make a choice of discarding one of the parse
trees by looking up the identifier in a symbol table.

The disadvantage of this approach is that a GLR parser will
produce multiple parse trees for all ambiguities in
your grammar—whether you know about them in advance or not.

## Hand-written parser

In case of a hand-written parser, you can do something
similar to the lexer hack but at the parser level.
As you parse, you construct a symbol table for types.
Whenever you encounter an identifier, you look it up in the
type symbol table.

This is how, for example, the
[hand-written Kotlin parser](https://github.com/JetBrains/kotlin/blob/23a4184e48bf1fe77ae27cbf121c51849157ecbf/compiler/frontend/src/org/jetbrains/kotlin/parsing/KotlinParsing.java#L1966) works.

<center>⁂</center>

Now let's move onto the language-level solutions.

The root of our problem is the following:
in the same context, we want to use "`<`" and "`>`"
symbols as both infix operators and as distinct parenthesis-like
delimiters.
So the ambiguity is inherent to the problem.

A language-level solution would be to use
a different syntax for the two cases.

## Scala solution

One example of this is Scala, which uses
square brackets as type parameters which avoids the problem
altogether:

```scala
x = Foo[Bar](1 + 2)

x = foo &lt; bar &gt; (1 + 2
```

While "`<`" and "`>`" are always parsed as infix operators,
"`[`" and "`]`" are always parsed as parenthesis-like
matching delimiters. So there's no confusion.

## Rust solution

Rust is one of the languages that continues the tradition
of using "`<`" and "`>`" symbols for both type parameters and infix
comparison operators.
However, in an expression context, it requires the
programmer to explicitly disambiguate them by using
a "`::<`" sequence. Consider:

```rust
let x: foo::Foo&lt;Bar&gt; = foo::Foo::&lt;Bar&gt;(1 + 2);
```

*(Having both type annotations is not necessary here, but nevertheless…)*

Inside the type annotation, you can write `Foo<Bar>`,
because it is a type-only context.
However, in an expression context, you need to write `Foo::<Bar>`.

<center>⁂</center>

You can classify the above solutions into syntactic and
semantic ones.

Syntactic solutions are those that make the decision
solely based on the syntax,
in our case:

* lexer whitespace sensitivity, and
* prioritized choice (PEG).

Both of these accept slightly different languages.

Semantic solutions are those that rely on a symbol table
for types to disambiguate:

* the lexer hack,
* generalized parsing, and
* hand-written parser.

Thes three solutions accept the same language.

If you're implementing an existing language,
you should carefully read the spec (if one exists)
to see which of the solutions could be applicable.
However, if you're designing a new language,
you have the power to come up with a syntax that is not
conceptually ambiguous.
Scala and Rust are good examples of this approach.
[&#9632;](/ "Home")

*This blog post was originally written by me
for [Datawire](https://www.datawire.io/distinguishing-type-constructors-arguments-comparison-expressions-parsing/)
and is re-published here with permission (and minor changes).*














<center>

<br/>
⁂


<style>
#cover {
  border: 1px solid black;
  width: 500px;
  color: black;
  display: block;
}

</style>



<h2>Did you know, I’m writing a book about compilers?</h2>


<div id=cover >
<a id=cover href=/compiling-to-assembly-from-scratch-the-book >

<br/>

<h1>Compiling to Assembly<br/><small>from Scratch<br/><small><em></em></small></small></h1>

— the book —<br/>
<br/>
<br/>

<img src=/dragon.png width=150 height=188 />

<br/>
<br/>
<br/>


<p>Vladimir Keleshev</p>

<em>TypeScript — ARM — Summer 2020</em>
<br/>
<br/>

</a>
</div>

</center>

