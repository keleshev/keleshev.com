---
title: Verbose Regular Expressions in JavaScript
fancy-title: "Verbose Regular Expressions<br/><small><small>in JavaScript</small></small><br/>"
date: 2020-05-02
---




Recently, I've been writing a lexer for my
[compiler book](/compiling-to-assembly-from-scratch-the-book)
in JavaScript.
Fortunately, JavaScript regular expressions are a useful tool for writing
lexers. However, I've been missing one feature that I particularly
like from Python: *verbose* regular expressions.

What are those?

Imagine we wanted to parse a floating-point number.
In Python, we could write a regular expression
like this:

```python3
re.compile(r"(0|[1-9][0-9]*)\.[0-9]*([eE][+-]?[0-9]+)?")
```

Or, we could instead supply a `VERBOSE` flag and write
the same regular expression like that:

```python
re.compile(r"""
  (0 | [1-9] [0-9]*)   # Integer part with no leading zeroes
  \.                   # Dot
  [0-9]*               # Fractional part (optional)
  ([eE] [+-]? [0-9]+)? # Exponent part (optional)
""", re.VERBOSE)
```
<!--pre>
re.compile(<em>r"""
  (0 | [1-9] [0-9]*)   # Integer part with no leading zeroes
  \.                   # Dot
  [0-9]*               # Fractional part (optional)
  ([eE] [+-]? [0-9]+)? # Exponent part (optional)
"""</em>, re.VERBOSE)
</pre-->

See the difference?

* Whitespace is ignored:
  you can space out your expression into logical chunks,
  just like your code.
  You can still match whitespace characters, but you need
  to escape them, for example, as "<code>\\ </code>"
  or "`[\ ]`".
* Comments: in this case, Python-style comments are allowed.
  This can help make your expressions much more readable!
* Multiline: expressions can span multiple lines.


JavaScript regexp engine doesn't have this feature.
But when did something like that stopped us before?!

## Raw strings

One problem with making verbose regular expressions
work in JavaScript is that the usual `/slash/`-style regexp literals
cannot be multiline in JavaScript.
However, what *can* be multiline in JavaScript is the
new ES2015 *template literals*:

```js
let example = `hello
world`;
```

We can use those.
The next problem is with escape sequences.
Often regexes have a lot of backslashes,
like `\.` for literal dot and `\s` for whitespace.
In JavaScript regexp literals, you can write them raw:
`/\.\s/`, but in a string or a template literal,
you need to escape them like this: `"\\.\\s"`.
This makes them less convenient for this use case.
Python has *raw* strings with `r"` prefix
and raw *multiline* strings with `r"""` prefix,
where escapes are not necessary.
But JavaScript, again, does not have this feature…
Or does it?

Turns out that template literals have a lesser-known
feature called *tags*.
Tags allow changing the meaning of a template literal.
Here's the syntax:

```js
let x = tag`hello`;
```

Which will expand *roughly* to the following:

```js
let x = tag({raw: ["hello"]});
```

I'm simplifying a bit: the signature of such a tag
function is a bit more complicated
(to handle raw and "cooked"/escaped strings
 and interpolation parameters),
but for our use, that's enough.

Using such tagged templates, we can implement Python's
raw strings as follows:

```js
function r(input) {
  return input.raw[0];
}

let example = r`\hello`;

console.assert(example === "\\hello");
```

And like other template literals they work as multiline too.

In fact, JavaScript has this "`r`" function built-in,
it is called `String.raw`:

```js
console.assert(String.raw`\hello` === "\\hello");

let r = String.raw;
console.assert(r`\hello` === "\\hello");
```

Tagged literals basically allow us to make
our own literals, for things like…
verbose regular expressions!

And that's what we'll do.
But first, we need to *design* them.

## Design

I don't think verbose regular expressions in
JavaScript should be exactly like those
in Python.
I think they should use JavaScript-style comments instead:

 * `// single-line`, *and*
 * `/* multi-line */`.

<!--
Next, Python verbose regular expressions
do not ignore whitespace inside character classes,
but I think it's quite useful.
You could write aregular expression like this one:

```js
[
  a-z  // Letters
  0-9  // Numbers
  _    // Undescore
]
```
-->

## Implementation

To implement verbose regular expressions in JavaScript
we'll use the tagged template literals as well as
a regular, *ahem*, regular expression:

```js
function verboseRegExp(input) {
  if (input.raw.length !== 1) { ❶
    throw Error("verboseRegExp: interpolation is not supported");
  }

  let source = input.raw[0]; ❷
  let regexp = /(?<!\\)\s|[/][/].*|[/][*][\s\S]*[*][/]/g;
  let result = source.replace(regexp, '');

  return new RegExp(result); ❸
}
```

We call our tag `verboseRegExp`.
Since it's already *verbose*, it doesn't hurt to be explicit
about what this new tag means.


<div class="circled-numbers">
1. We add a guard that checks that only one string
is supplied.
That means that the string has no interpolations.
It would be interesting to see what string interpolation
could give us in this case, but let's ignore it now.

2. Next, we extract the raw string from the input parameter.
Using a regular expression, we remove the comments
and the whitespace (except for whitespace escaped with
a backslash).
Too bad we can't use a verbose regular expressions here,
as you know, the cobbler's son has no shoes.

3. Finally, we construct the regular expression out of the
resulting string.
</div>

## Examples

Now, we can finally use it!
And, of course, the first example we'll use will be the
regular expression we just used to implement our verbose regular expressions:

```js
let example1 = new RegExp(verboseRegExp`
    (?<!\\) \s             // Ignore whitespace, but not
                           // when escaped with a backslash.
  | [/][/] .*              // Single-line comment.
  | [/][*] [\s\S]* [*][/]  // Multi-line comment.

  // Note: /[\s\S]/ is same as /./s with dot-all flag (s),
  // but we can't use dot-all here since that would break
  // the single-line comment case.
`, "g");
```

This also gives us a chance to fully explain the meaning of that regular expression.

One thing that the new regular expression syntax does not
allow us is to specify the *flags* (such as `g` for *global*)
directly.
But since it's *verbose*, it doesn't hurt to wrap
it into another `RegExp` call and pass `"g"` explicitly, like we did above.

Next example covers the parsing of a floating-point
number that we discussed in the beginning:

```js
let example2 = verboseRegExp`
  (0 | [1-9] [0-9]*)   // Integer part with no leading zeroes
  \.                   // Dot
  [0-9]*               // Fractional part (optional)
  ([eE] [+-]? [0-9]+)? // Exponent part (optional)
`;
```

I hope that this lightweight technique
will make your regular expressions more readable!

## Source code

This code, together with some unit tests,
is available as a
[GitHub gist](https://gist.github.com/keleshev/c49465caed1f114b2bb3f2b730e221ca).

