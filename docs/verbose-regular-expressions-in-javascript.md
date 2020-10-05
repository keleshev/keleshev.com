---
title: Verbose Regular Expressions in JavaScript
---


<style> #home { position:absolute; line-height: inherit; } </style>

<span id=home><a title=Home href=/>☰</a></span>

<h1>
  Verbose Regular Expressions<br/>
  <small><small>in JavaScript</small></small><br/>
</h1>

<center>2020-05-02</center>

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

<!--
re.compile(r"""
x (0 | [1-9] [0-9]*)   # Integer part with no leading zeroes
  \.                   # Dot
  [0-9]*               # Fractional part (optional)
  ([eE] [+-]? [0-9]+)? # Exponent part (optional)
""", re.VERBOSE)
-->
<pre>
re.compile(<em>r"""
  (0 | [1-9] [0-9]*)   # Integer part with no leading zeroes
  \.                   # Dot
  [0-9]*               # Fractional part (optional)
  ([eE] [+-]? [0-9]+)? # Exponent part (optional)
"""</em>, re.VERBOSE)
</pre>

See the difference?

* Whitespace is ignored:
  you can space out your expression into logical chunks,
  just like your code.
  You can still match whitespace characters, but you need
  to escape them with a backslash, for example: "`\    `  "
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
let example = <em>`hello
world`</em>;
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
let x = tag`<em>&#96;hello&#96;</em>`;
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

let example = r`<em>&#96;\hello&#96;</em>`;

console.assert(example === "\\hello");
```

And like other template literals they work multiline too.

In fact, JavaScript has this "`r`" function built-in,
it is called `String.raw`:

```js
console.assert(String.raw`<em>&#96;\hello&#96;</em>` === "\\hello");

let r = String.raw;
console.assert(r`<em>&#96;\hello&#96;</em>` === "\\hello");
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
    throw Error(<em>&#34;verboseRegExp: interpolation is not supported&#34;</em>);
  }

  let source = input.raw[0]; ❷
  let regexp = /(?&lt;!\\)\s|[/][/].*|[/][*][\s\S]*[*][/]/g;
  let result = source.replace(regexp, '');

  return new RegExp(result); ❸
}
```

We call our tag `verboseRegExp`.
Since it's already *verbose*, it doesn't hurt to be explicit
about what this new tag means.

❶ We add a guard that checks that only one string
is supplied.
That means that the string has no interpolations.
It would be interesting to see what string interpolation
could give us in this case, but let's ignore it now.

❷ Next, we extract the raw string from the input parameter.
Using a regular expression, we remove the comments
and the whitespace (except for whitespace escaped with
a backslash).
Too bad we can't use a verbose regular expressions here,
as you know, the cobbler's son has no shoes.

❸ Finally, we construct the regular expression out of the
resulting string.

## Examples

Now, we can finally use it!
And, of course, the first example we'll use will be the
regular expression we just used to implement our verbose regular expressions:

```js
let example1 = new RegExp(verboseRegExp`
    (?&lt;!\\) \s             // Ignore whitespace, but not
                           // when escaped with a backslash.
  | [/][/] .*              // Single-line comment.
  | [/][*] [\s\S]* [*][/]  // Multi-line comment.

  // Note: /[\s\S]/ is same as /./s with dot-all flag (s),
  // but we can't use dot-all here since that would break
  // the single-line comment case.
`, "g");
```

This also gives us a chance to explain well the
meaning of that regular expression.

One thing that the new regular expression syntax does not
allow us is to specify is *flags* (such as `g` for *global*)
directly.
But since it's *verbose*, it doesn't hurt to wrap
it into another `RegExp` call and pass `"g"` explicitly.

<center>⁂</center>

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

## Code

This code, together with some unit tests,
is available as a
[GitHub gist](https://gist.github.com/keleshev/c49465caed1f114b2bb3f2b730e221ca).

<center>⁂</center>

I hope that this lightweight technique
will make your regular expressions more readable,
and I hope you've learned a thing or two today!
[&#9632;](/ "Home")



<center>


⁂

<style>
#cover {
  border: 1px solid black;
  width: 500px;
  color: black;
  display: block;
}

</style>



<h2>Did you know about my upcoming book?
</h2>


<div id=cover >
<a id=cover href=/compiling-to-assembly-from-scratch-the-book >

<br/>

<h1>Compiling to Assembly<br/><small>from Scratch<br/><small><em></em></small></small></h1>

— the book —<br/>
<br/>
<br/>

<img src=/dragon.png width=256 height=260 />

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
