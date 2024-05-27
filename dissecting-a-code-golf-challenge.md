---
title: "Dissecting a Code Golf Challenge"
fancy-title: "Dissecting a Code Golf Challenge"
date: 2014-03-23
---

You probably know, *code golf* is a "sport" of writing
a program which solves a task with as little number
of characters of source code as possible.

At the local Python meetup, Brian Lauridsen
presented a code golf challenge. The challenge is called
*grid computing* and was available at
[codegolf.com](http://codegolf.com), which at the moment
of writing is down. Here is the approximate description
of the challenge:

> Write a program that expects a 10-by-10 matrix from
> standard input. The program should compute sum of each
> row and each column and print the highest of these
> numbers to standard output.
>
> An example input:
>
>     01 34 46 31 55 21 16 88 87 87
>     32 40 82 40 43 96 08 82 41 86
>     30 16 24 18 04 54 65 96 38 48
>     32 00 99 90 24 75 89 41 04 01
>     11 80 31 83 08 93 37 96 27 64
>     09 81 28 41 48 23 68 55 86 72
>     64 61 14 55 33 39 40 18 57 59
>     49 34 50 81 85 12 22 54 80 76
>     18 45 50 26 81 95 25 14 46 75
>     22 52 37 50 37 40 16 71 52 17
>
> Expected output:
>
>     615

The challenge is very tempting by its simplicity. However,
according to codegolf.com, the best solution in Python
was written in only 73 characters. At the meetup we
got it down to 78 characters, but not less. So the weekend
after the meetup I immersed into this challenge to
get it down to 73. And here are the results.

> **Spoiler alert:** this page contains the 73 character solution.

Solving the puzzle
------------------

Let's see what a *naïve* solution can look like in Python:

```python
import sys

# Parse matrix.
matrix = []
for line in sys.stdin.read().splitlines():
    row = []
    for digits in line.split(' '):
        number = int(digits)
        row.append(number)
    matrix.append(row)

# Row sums.
all_sums = []
for row in matrix:
    all_sums.append(sum(row))

# Column sums.
for i in range(10):
    column = []
    for row in matrix:
        column.append(row[i])
    all_sums.append(sum(column))

print(max(all_sums))
```

*Total: 446 characters.*

I hope you are displeased by this code as much as I am.
Let's gradually improve it.

File-like objects have a `.readlines()` method, so we could
call it instead of `.read().splitlines()`.  However,
you might know that file-like objects support the iterator
protocol, so you can iterate over them directly:

```python
for line in sys.stdin:
    ...
```

Also you might know that calling `.split()` on a string
will split over any whitespace, so no need to call
`.split(' ')`.

Next, using list-comprehensions instead of for loops
tightens up the code considerably:

```python
import sys

matrix = [[int(digits) for digits in line.split()]
          for line in sys.stdin]

row_sums = [sum(row) for row in matrix]

column_sums = [sum([row[i] for row in matrix])
               for i in range(10)]

print(max(row_sums + column_sums))
```

*Total: 256 characters.*

Some people will already claim that this is *too* tight
and unreadable, but I think it is still sensible.

Next, using `map` instead of list comprehensions will
save us some characters. We can use:

* `map(int, line.split())` to parse each line,
* `map(sum, matrix)` for `row_sums`.

However, there is some duplication between `row_sums`
and `column_sums`. We could pull out summation,
and apply it in the last step instead:

```python
import sys

matrix = [map(int, line.split())
          for line in sys.stdin]

rows = [row for row in matrix]

columns = [[row[i] for row in matrix]
           for i in range(10)]

print(max(map(sum, rows + columns)))
```

*Total: 197 characters.*

Party trick
-----------

Now, the above code is silly, because `rows` is the same as `matrix`,
and `columns` is the same matrix, but transposed. We could
use a library like `numpy` to transpose a matrix, but using
libraries is against the rules of code golf.
Otherwise you could just
write libraries that solve a challenge in one function call.

But you might know this "party trick", that `zip(*matrix)`
transposes a matrix. If you didn't know about this,
stop and think about it for a minute.

```python
import sys

matrix = [map(int, line.split())
          for line in sys.stdin]

print(max(map(sum, matrix + zip(*matrix))))
```

*Total: 113 characters.*

Now let's go all-dirty on this and remove all unnecessary
whitespace, and make every variable a single letter.

```python
import sys
m=[map(int,l.split())for l in sys.stdin]
print(max(map(sum,m+zip(*m))))
```

*Total: 83 characters.*

*Now*, we are much closer to our goal of *73* characters.

Knowing your pythons
--------------------

One way to save 5 characters would be to use a built-in
function called `input`, which reads a single line from
standard input. However, this is when we realize that
the codegolf.com checks the solutions using Python 2.5.
That forces us to use `raw_input` instead, saving a single
character instead of 5.

On the other hand, Python 2 allows to drop parenthesis
of `print` call, so we save another character:

```python
m=[map(int,raw_input().split())for _ in range(10)]
print max(map(sum,m+zip(*m)))
```

*Total: 81 characters.*

Obscured iteration
------------------

Using `raw_input` forced us
to use `range(10)` instead of iterating over lines.
How can we mitigate this?! Another way to iterate 10 times
would be to iterate over a collection of length 10.
We can get this collection by multiplying a list with
a single item by 10:

```python
m=[map(int,raw_input().split())for _ in[0]*10]
print max(map(sum,m+zip(*m)))
```

*Total: 77 characters.*

Hexdump
-------

However, we still haven't used one important code golf trick.
If you do a `hexdump` of our program, you can see that
we have a trailing newline, which is usually added by the
editor. You might also discover that your editor is
using `\r\n` instead of `\n`.

    $ hexdump -c grid_challenge.py | cut -c '9-'
    m  =  [  m  a  p  (  i  n  t  ,  r  a  w  _  i
    n  p  u  t  (  )  .  s  p  l  i  t  (  )  )  f
    o  r     _     i  n  [  0  ]  *  1  0  ] \n  p
    r  i  n  t     m  a  x  (  m  a  p  (  s  u m
    ,  m  +  z  i  p  (  *  m  )  )  ) \n

Yep, we have a trailing `\n`. Let's write a script that
removes it from our programs, and now we are down to...

*Total: 76 characters.*

Leaked variable
---------------

And here the *really* hard part starts. I have spent many
hours trying to reduce this number. And it got really
nasty.

One little known misfeature of Python 2 is that
it leaks variable bindings from comprehensions
(as well as `except` clauses). This was fixed in Python 3.
Here's some code to illustrate the issue:

<pre>
$ python3
>>> [x <b>for</b> x in range(10)]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> x
<em>Traceback (most recent call last):
  File "&lt;stdin&gt;"</em><em>, line 1, in &lt;module&gt;
NameError: name 'x' is not defined</em>
</pre>

```python
$ python2
>>> [x for x in range(10)]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> x
9
```

You see, `x`—"leaked" from inside the list comprehension
and was available in the outer scope with its last assigned value.

How can we use this?! Well, right now we are not using
the list comprehension variable at all. But instead we
could put it to some use... We are calling `map` twice.
It would be so handy if we could put it into a variable,
without paying the cost of an explicit assignment…

```python
m=[_(int,raw_input().split())for _ in[map]*10]
print max(_(sum,m+zip(*m)))
```

*Total: 74 characters.*

Here we created a list of 10 `map` functions, which allowed
us to assign `map` to the undescore (`_`) variable and save 3 characters in total.
But we are still behind the
world's best 73 character solution.

The last drop
-------------

One less obscure feature of `raw_input` is that it takes
an optional argument called `prompt`, which gets printed
as a prompt before it reads a line from standard input.
Let's see if we gain anything by assigning `raw_input` to
the undescore (`_`), instead of `map`, and then...

```python
m=[map(int,_().split())for _ in[raw_input]*10]
_(max(map(sum,m+zip(*m))))
```

*Total: 73 characters.*

Yes! By using `raw_input` instead of `print` we saved the
last character and reached the world record for this
challenge.

I bet you have learned something new about Python today.
[☰](/ "Home")

## Citation

<small>
```
@misc{Keleshev:2014-1,
  title="Dissecting a Code Golf Challenge",
  author="Vladimir Keleshev",
  year=2014,
  howpublished=
    "\url{https://keleshev.com/dissecting-a-code-golf-challenge}",
}
```
</small>
