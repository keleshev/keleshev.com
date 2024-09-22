---
title: "5. Parser Combinators • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 5</small></small><br/>Parser Combinators<br/><br/></h1>
```

\chapter{Parser Combinators}
\includegraphics{chapter-illustrations/5b.png}
\newpage

A parser is a function that converts some textual source into structured data.
In our case, it converts a program's source into the corresponding AST.

There's a myriad of parsing techniques and approaches.
Which one to choose often depends on the source language and its syntactic features.

The technique that we'll use is called *parser combinators*.
We'll also use some *regular expressions* since they are so handy in JavaScript.

The idea of parser combinators is to create a small number of *primitive* parsers that could be *combined* into more complex parsers.
Each primitive parser is very simple and barely does anything useful on its own, but combining those we can parse increasingly complex languages.

Parser combinators can be used to implement pretty much any parsing algorithm.
They can parse immediately, or produce a data structure representing grammar that is used later.
They can even be used for code generation.
In practice (and historically), many parser combinators are *scanerless* (token-less), *greedy*, *backtracking*, and with *prioritized choice*.
(We'll get to what these mean in a minute).
And our parsing combinators will be no exception.

Parsing combinators are my go-to technique when I need to parse something "by hand": they are easy to implement and are powerful.
After implementing a few primitive combinator functions, you get something comparable to a full-blown parser generator.

## Lexing, scanning, or tokenization

Lexing, scanning, and tokenization are all synonymous when talking about parsing.
They refer to convertion of the source program into an intermediate representation called *token stream*.
The token stream structure consists of individual "words" of our program, also called *tokens*, *lexemes*, or *lexical elements*.
This terminology originated in linguistics, the field which pioneered grammars and parsing.

\newpage

A token stream is a linear representation, unlike the tree-like representation of AST.

A lexer would convert source like `x + y` into linear token stream like this:

```js
[
  new TokenId("x"),
  new TokenOperator("+"),
  new TokenId("y"),
]
```

And only then a parser would convert this to an AST like `new Addition(new Id("x"), new Id("y"))`{.js}.

We've represented it using an array, but more often, it is some kind of lazy or streaming collection.

This is all to say that we won't use a lexer: our parser will be *scannerless*.
The way to think about scannerless parsing is you treat each character as a token.
However, we will still use the word token when we talk about parsing single logical lexical elements.
We also won't go into details of the benefits and shortcomings of lexing or scannerless parsing.
Here we've picked scannerless because of the implementation simplicity.


## Grammars

When making parsers, we want to discuss what language constructs those parsers can recognize.
For that, we will use *grammars*.
There are several notations to describe grammars.
You might have heard about *Extended Backus-Naur Form* (EBNF).
In our case, we will use *Parsing Expression Grammar* (PEG) notation.
PEG notation is a good fit for us because it's designed for *scannerless*, *greedy*, *backtracking* parsers, and can express *prioritized choice*.
It borrows notation from EBNF and regular expressions.

As we introduce each parser combinator, we will also show the corresponding grammar.
You will see that our parser combinators are designed to mimic the grammar notation.


## Interface

Let's say that a parser is an object with a `parse` method that takes something called `Source` and returns either something called `ParseResult` or `null`{.js}.

```js
interface Parser<T> {
  parse(s: Source): ParseResult<T> | null;
}
```

TypeScript allows us to explicitly say that the `parse` method may return `null`{.js}, and it will also enforce this in its *strict null checking* mode.

What are `Source` and `ParseResult`?
Why couldn't we use `string` for the source?

When parsing, we need to keep track of the string that we parse and the location in the string where we are currently matching.
Thus, `Source` is a pair consisting of:

  * the string that we parse, and
  * the index into that string that points to where we are parsing right now.

<!-- -->

```js
class Source {
  constructor(public string: string,
              public index: number) {}
  …
}
```

But also, `Source` allows us to avoid having tight coupling with the `string` type.
For example, we can later make another implementation of `Source` that lazily reads from a file.

`Source` will be quite efficient for our use case since most `Source` objects will share the same `string` during parsing.

What about `ParseResult`?
It is a simple data object that can hold some value produced by the parser and the source with the updated index position.
The `value` will often be an `AST`, in our case.
The `source` signifies where the parser left off, so another parser can continue from there.

\newpage

```js
class ParseResult<T> {
  constructor(public value: T,
              public source: Source) {}
}
```

However, parsers are allowed to return not only `ParseResult`, but also `null`{.js}.
When returning `null`{.js} parser signifies that it didn't match anything.
It is not an error: during a single pass, many rules will not match, but others will.

Right now, `Source` doesn't have any operations defined.
Many choices are possible.
One of them is to expose a `match` method, very similar to `string.match` that takes a regular expression.
The difference with `string.match` is that we need to match from a particular `source.index` position.
This is possible with so-called "sticky" regular expressions.

Sticky regular expressions in JavaScript are specified with a flag "`y`", like this: `/hello/y`.
They are special in the way that they have a `lastIndex` property.
By setting this property to some index, we can control where the regular expression will be matched.
It's an odd design, but it works for us.
Other programming languages have different ways to match a regular expression from a particular index.

Let's write our `match` method:

```js
class Source {
  constructor(public string: string,
              public index: number) {}

  match(regexp: RegExp): (ParseResult<string> | null) {
    console.assert(regexp.sticky);
    regexp.lastIndex = this.index;
    let match = this.string.match(regexp);
    if (match) {
      let value = match[0];
      let newIndex = this.index + value.length;
      let source = new Source(this.string, newIndex);
      return new ParseResult(value, source);
    }
    return null;
  }
}
```

First, we assert that the regexp we got is sticky; otherwise, this will not work.
Then we set `lastIndex` on the regexp to match from the source index.
Then we delegate to `string.match` method to do the matching.
If the match object is `null`{.js}, we return `null`{.js}: we couldn't match the regular expression.
Otherwise, we got a regexp "match" object.
It is an array-like object where the first item is the substring that matched the regular expression.
We use that substring in two ways:
First, it's the value of the `ParseResult` that we use.
Second, we count the length of the matched string to advance the new `Source` index that we return as the second component of `ParseResult`.

As you can see, `Source` already *almost* satisfies our `Parser` interface.

A natural way to implement parser combinators that satisfy the `Parser` interface in TypeScript would be to create a class for each parser, with different `parser` methods.
However, since `Parser` interface has only one method, and many of our parser combinators will have one-liner implementations, let's use a more light-weight approach.
Instead, we'll have a single `Parser` class that takes `parse` method (as an arrow function) as a parameter:

```js
class Parser<T> {
  constructor(
    public parse: (s: Source) => (ParseResult<T> | null)
  ) {}

  …
}
```

## Primitive combinators

Now, let's start defining the *primitive* parser combinators.
Some of them will be `Parser` instance methods; some will be static methods.
We pick one or another purely based on notation: whether `f(x)` or `x.f()` is more readable for each combinator.
While making this choice, we will try to mimic the corresponding grammar.

## Regexp combinator

Our first combinator called `regexp` creates a parser that matches a regexp.
It only delegates to the `source.match` method that we've just defined.

```js
class Parser<T> {
  …

  static regexp(regexp: RegExp): Parser<string> {
    return new Parser(source => source.match(regexp));
  }
}
```

<!--

X: It took me more time to understand section 5.5 compared to what I read so far. I think there’s a transition missing between the regexp combinator and the hello example. Also it might have been nice to show an example of what it parses. hello1 for example. The last paragraph’s structure seemed muddy to me.

-->

When using this combinator, we must remember to pass "sticky" regular expressions with the "`y`" flag.
Otherwise, the assertion that we defined earlier will remind us.

```js
let hello = Parser.regexp(/hello[0-9]/y);
```

The corresponding PEG grammar is:

```
hello <- "hello" [0-9]
```

The arrow defines a grammar rule called `hello`.
As you can see, the PEG notation borrows from regular expression notation.
A string in double-quotes matches literally, while `[0-9]` is a character class, a concept borrowed from regular expressions.
Outside the quotes and the character class, whitespace does not matter.

Let's try to use our `hello` parser to parse a string:

```js
let source = new Source("hello1 bye2", 0);
let result = Parser.regexp(/hello[0-9]/y).parse(source);

console.assert(result.value === "hello1");
console.assert(result.source.index === 6);
```

Here we create a new source from string `"hello1 bye2"`.
We want it to parse from the beginning so we set the source index to zero.
We call `parse` with the constructed source, and we get back a `ParseResult` object.
Then we assert that the value being parsed is `"hello1"` and the resulting source index has advanced to column six, where the rest of the string is located: `" bye2"`.

## Constant combinator

Next combinator might seem a little silly: it's a parser that always succeeds, returns a constant value, does not consume any input (so, does not advance the source).
We call it `constant`.
How is it good for anything?
Soon, you will see.
For now, let's say that it allows, when combined with other parsers, to change the return value (and the type) of a parser.

```js
class Parser<T> {
  …

  static constant<U>(value: U): Parser<U> {
    return new Parser(source =>
      new ParseResult(value, source));
  }
}
```

In PEG it would correspond to an empty string:

```
empty <- ""
```

The notation does not concern itself with what value is produced, only with what string is recognized.


## Error combinator

Next is `error`: a parser that just throws an exception.
The exception is not intended to be handled.
It is expected to terminate the program.

```js
class Parser<T> {
  …

  static error<U>(message: string): Parser<U> {
    return new Parser(source => {
      throw Error(message);
    });
  }
}
```

There's no correspondence with PEG notation.

\newpage

> **Explore**
>
> A better implementation of the `error` combinator would inspect the source, convert the source index into a line-column pair, and display it together with the offending line and some context.

We can use these combinators with a fully qualified names, like `Parser.regexp`, or we can "import" them into the current namespace:

```js
let {regexp, constant, error} = Parser;
let hello = regexp(/hello[0-9]/y);
```

From now on, we will assume that the names of the parser combinators we define are imported, and we don't need to qualify them.

## Choice operator

Next primitive parser combinator is the *choice operator* that we define as the `or` instance method on parsers.
It allows us to select between two (or more) alternative parser choices.
Unlike the previous primitive combinators, this is an instance method, not a static method.
We use an instance method here purely for syntactic reasons.
We would like to write `x.or(y).or(z)`, instead of `or(or(x, y), z)`, so it mimics the corresponding PEG grammar: `x / y / z`.

A parser like `left.or(right)` first tries to parse using the `left` parser.
If successful, the result is returned.
If not, the `right` parser is tried, and its result is returned.

```js
class Parser<T> {
  …

  or(parser: Parser<T>): Parser<T> {
    return new Parser((source) => {
      let result = this.parse(source);
      if (result)
        return result;
      else
        return parser.parse(source);
    });
  }
}
```

Such choice operator is called *prioritized choice* operator.
In contrast with *unordered choice* operator, it tries the alternative parsers in a (prioritized) order from left to right.

PEG notation helps us be precise about the fact that we use prioritized choice by using forward slash (`/`) as opposed to the unordered choice operator, which is usually denoted with a horizontal bar (`|`).

Unordered choice can be handled in different ways too: a parser could explore several choices simultaneously, or the choice that could be determined unresolvable by looking at one (or *n* characters) could be rejected outright, ahead of any parsing.

The choice operator is one of the central topics in parsing, and its choice is often the decisive factor in parser performance and recognition power.

Given a parser like `left.or(right)`, we say that it *backtracks* because it will try parser `left` and, if that does not succeed, will *backtrack* (or return) to the same source index and try the `right` parser.
We say that our parser has *unlimited look-ahead* because it will try to parse `left` completely, no matter how long the match is, in other words, without any *limit*.
Other techniques look ahead at one (or *n* characters, or tokens) to decide which choice to take.

Theoretically, the way we implemented our choice operator is not very efficient and could be improved with caching.
However, if we take some care with combining our parsers, it could be a non-problem.
The key is not to combine parsers that can parse the same long prefix, but instead combine alternative parsers so that they can quickly recognize that they don't match and move to the next one.

Consider a parser constructed from the following two: one matches a hundred consecutive characters "a" followed by a single "b", and another matches a hundred consecutive characters "a" followed by a single "c".
Given an input that matches the latter, it will have to scan one hundred characters *twice*:

```js
regexp(/a{100}b/y).or(regexp(/a{100}c/y))
```

On the other hand, if we have one parser that parses a letter, and another one that parses a digit, we can combine them with `or` and it takes only one character to check if the first parser matches or not, before moving to the next parser.

```js
let letterOrDigit =
  regexp(/[a-z]/y).or(regexp(/[0-9]/y));
```

This parser can be described with the following grammar:

```
letterOrDigit <- [a-z] / [0-9]
```


## Repetition: zero or more

The next primitive parser combinator is `zeroOrMore` that handles repetition.
Given a parser that returns some result, it will return a new parser that returns an array of results, instead.
The implementation is as follows.

```js
class Parser<T> {
  …

  static zeroOrMore<U>(
    parser: Parser<U>,
  ): Parser<Array<U>> {
    return new Parser(source => {
      let results = [];
      let item = null;
      while (item = parser.parse(source)) {
        source = item.source;
        results.push(item.value);
      }
      return new ParseResult(results, source);
    });
  }
}
```

We apply the same parser several times in a `while` loop.
Each time we advance the `source` and push the resulting value into an array.
As soon as one of the parses does not match and returns `null`{.js}, we return that array as the result in a new `ParseResult` object that bundles the last `source`.

For example, this parser will match zero or more letters or digits, given `letterOrDigit` that we have just defined.

```js
let someLettersOrDigits = zeroOrMore(letterOrDigit);
```

This combinator function corresponds to the star (`*`) operator in PEG, similar to the regular expressions notation.

```js
someLettersOrDigits -> letterOrDigit*
```

We can also inline `letterOrDigit` and rewrite this as:

```js
someLettersOrDigits -> ([a-z] / [0-9])*
```

We say that our `zeroOrMore` or "star" operator is *greedy*.
It matches the PEG semantics, but differs from regular expressions.
A regular expression like `a*a` will match one or more letters `a`.
However, `a*a` in PEG (and our parser combinators) will never match anything: the `a*` part of the expression will "greedily" consume input as long as it can match, and without any respect for what follows it.

## Bind

The next parser combinator is an interesting one.
It is another key combinator, on par with the choice operator.
As the name alludes, it *binds* a value that is being parsed to a name.
By binding a value to a name, we can manipulate and construct values that our parser produces.

```js
class Parser<T> {
  …

  bind<U>(
    callback: (value: T) => Parser<U>,
  ): Parser<U> {
    return new Parser((source) => {
      let result = this.parse(source);
      if (result) {
        let value = result.value;
        let source = result.source;
        return callback(value).parse(source);
      } else {
        return null;
      }
    });
  }
}
```

It takes a callback, which usually will be an arrow function.
The callback takes the parsed result as the parameter and returns a new parser that should continue parsing.
This way, we can combine several parsers and bind their values to construct a new return value.

For example, here we are constructing a parser for comma-separated pairs of numbers, like `"12,34"`.

```js
let pair =
  regexp(/[0-9]+/y).bind((first) =>
    regexp(/,/y).bind((_) =>
      regexp(/[0-9]+/y).bind((second) =>
        constant([first, second]))));
```

We bind the first numeric parser to the `first` parameter. We ignore the result of the comma regexp (by binding it to an underscore), then bind the second numeric regexp to the `second` parameter.
From those, we construct an array, and we "return" this array by constructing a constant parser.

The corresponding grammar is:

```
pair <- [0-9]+ "," [0-9]+
```

As always, the grammar ignores the value of the parser constructs; it is only concerned with which language constructs it can recognize.

## Non-primitive parsers

In the first example of using `bind`, we have seen two patterns that keep repeating when you use `bind` in practice.
That's why we will introduce them now as non-primitive parsers.

## And and map

The first repeating pattern is using `bind`, but ignoring the value.
It effectively creates a sequence of parsers.
We call this non-primitive combinator `and`.
It allows to sequence parsers just like `bind`, but without binding a value to a name:

\newpage

```js
class Parser<T> {
  …

  and<U>(parser: Parser<U>): Parser<U> {
    return this.bind((_) => parser);
  }
}
```

The next pattern that we'll see a lot is binding name only to return a constant parser immediately.
We call it `map`.

```js
class Parser<T> {
  …

  map<U>(callback: (t: T) => U): Parser<U> {
    return this.bind((value) =>
      constant(callback(value)));
  }
}
```

It is worth mentioning that this `map` method is in a way similar to the `array.map` method.

* * *

Now, let's try to rewrite our pair parser using the new methods:

```js
let pair =
  regexp(/[0-9]+/y).bind((first) =>
    regexp(/,/y).and(
      regexp(/[0-9]+/y)).map((second) =>
        [first, second]));
```

Note that the value produced by the left parser in `left.and(right)` is ignored.
If you don't want to ignore it, you need to `bind` it.

Writing code in this way is not unlike writing code that involves JavaScript promises.
It can be tricky sometimes, but fortunately, given a grammar, we can make the corresponding parser almost mechanically.

\newpage

Let's look at it in another way.
Let's say we have in mind a grammar, like our pair grammar:

```
pair <- [0-9]+ "," [0-9]+
```

Say, we want to produce a parser for it.
We use `let`{.js} to define the named rule, and use the `and` method for all sequences (and the `or` method for any alternatives):

```js
let pair =
  regexp(/[0-9]+/y).and(
    regexp(/,/y).and(
      regexp(/[0-9]+/y)));
```

And now, we should think about which values we want to extract.
We want to extract the two numeric values, so we replace `and` with `bind` for them:

```js
let pair =
  regexp(/[0-9]+/y).bind((first) =>
    regexp(/,/y).and(
      regexp(/[0-9]+/y).bind((second) => …)));
```

And in the last bind we construct the value we want with the `constant` parser:

```js
let pair =
  regexp(/[0-9]+/y).bind((first) =>
    regexp(/,/y).and(
      regexp(/[0-9]+/y).bind((second) =>
        constant([first, second])));
```

We're done, but if we want, we can replace the second `bind` with `map` since it returns a constant parser:

```js
let pair =
  regexp(/[0-9]+/y).bind((first) =>
    regexp(/,/y).and(
      regexp(/[0-9]+/y).map((second) =>
        [first, second])));
```

<!--
It can seem first that `map` and `and` don't have a tremendous utility.
And I agree with that.
What's important is to get fluent with using `bind`, and when you get comfortable with that, use `map` and `and` where it improves readability for you.
-->

\newpage 

## Maybe

The `maybe` combinator allows us to parse something, or return `null`{.js}, optionally.
We can achieve this by combining the `or` operator with `constant(null)`{.js} parser:

```js
class Parser<T> {
  …

  static maybe<U>(
    parser: Parser<U | null>,
  ): Parser<U | null> {
    return parser.or(constant(null));
  }
}
```

Here we are optionally parsing a letter or a digit:

```js
let maybeLetterOrDigit = maybe(letterOrDigit);
```

This combinator corresponds to the "`?`" operator in PEG, also similar to the regular expressions notation:

```js
maybeLetterOrDigit <- letterOrDigit?
```

Like in PEG, and unlike regular expressions, our `maybe` combinator is *greedy*.

Often it is useful to have a different default rather than `null`{.js}, for example, an empty array.
In those cases we can simply say `parser.or(constant([]))`{.js}.

## Parsing a string

Although each parser has a `parse` method, this method is more convenient for composing parsers rather than using them in practice.
So let's define a helper method, that's a little different, called `parseStringToCompletion`.

\newpage

```js
class Parser<T> {
  …

  parseStringToCompletion(string: string): T {
    let source = new Source(string, 0);

    let result = this.parse(source);
    if (!result)
      throw Error("Parse error at index 0");

    let index = result.source.index;
    if (index != result.source.string.length)
      throw Error("Parse error at index " + index);

    return result.value;
  }
}
```

As the name suggests, instead of taking a `Source` object, this method takes a string.
It makes it more convenient for testing and using the resulting parsers.
This method creates a `Source` for you and calls the `parse` method.
However, unlike the `parse` method, it throws an exception if the result could not be parsed, and in case the parsing did not consume all of the input string.
It also unpacks the `ParseResult` to give us only the resulting value.

* * *

Now that we have learned how to construct parsers, let's make the parser pass for our baseline compiler!

\newpage

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}

```{=html}
<center><a href="./06-first-pass-the-parser#fold">Next: Chapter 6. First Pass: The Parser</a></center>
```
