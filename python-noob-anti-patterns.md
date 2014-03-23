Python noob anti-patterns
=========================

Last summer Finn Årup Nielsen
([@fnielsen](https://twitter.com/fnielsen)\)
invited me to be a teaching asistant at his course called
*Data mining using Python* at Technical University of Denmark.

Teaching is something that I’m really excited about, so even though
TA is usaly a student’s job, I could not resist.

Bad influence of other languages
------------------------------------------------------------

Students were required to know at least one programming
language before joining this course. Even though, there were
a few students who knew SML and Haskell, most of them were
only exposed to C and Java.

Because C and Java are more low-level languages, some things
that are idiomatic in them are actualy bad practices in Python.

# Using an index variable while looping

    for (int i = 0; i < LENGTH; i++) {
        process(items[i])
    }

    Getters and setters
    Mixing up class and instance variables
    Emulating end’s
    Using indexes for iteration: `for i in range(len(...))`
    Using `import *`
    If-else instead of dictionary look-ups


Not using pyflakes
------------------------------------------------------------
    Unused variables, imports

Not following PEP 8
    Long lines

Not using static analysis tools
------------------------------------------------------------

Documentation
------------------------------------------------------------
    Comments instead of docstrings
    Docstrings in wrong places
    Using JDoc
    Excessive commenting
    Not following PEP 257
    Unrepeatable doctests

Subtleties
------------------------------------------------------------
    Not subclassing `object`
    Unnecessary parenthesis
    Ennecessary backslashes
    Forgetting `if __name__ == '__main__'`
    Using double underscores for private methods
    Use of `exit` instead of `sys.exit`
    Integer division might be a bug
    Writing `== None`




Language-agnostic anti-patterns
------------------------------------------------------------
    Excessive nesting
    Single-letter variables
    Unreachable code
    Using numbers for versions
        import sysconfig
        if float(sysconfig.get_python_version()) < 3.1:
            exit('your version of python is below 3.1')
    Returning `True` or `False` literals
    Hardcoded constants (paths, values)
    Storing secrets in code
    Manual parsing of nested structures
    No functions

System-facing
------------------------------------------------------------
    Printing to `stdout` instead of `stderr`
    Not returning exit-codes on error
    Manually parsing `sys.argv`
    Wrong or now shebang (#!/macports/bin/python)


Exceptions
------------------------------------------------------------

### Putting a lot of code inside try-except


### Catching exception and rasing a different one


### Catch-all try-except blocks... pass


Not knowing standard library
------------------------------------------------------------
    Not knowing about `collections.Counter` (or `nltk.FreqDist`)
    Using `randint` instead of other alternatives (off-by-one often)
    Overuse of `copy` and `deepcopy`

Not knowing built-ins (also len)
------------------------------------------------------------
    `try-except: KeyError` instead of `get`
    Using `sorted` instead of `min` or `max`
    Doing `list(reversed(sorted(...)))`

Reinventing magic methods (write, delete)
Weird anti-patterns: `for _ in range(1): ... break`
Local imports
Using magic methods directly
Not using context-managers, list-comprehensions
Functions and methods for printing objects
Printing instead of returning a value
Messing up encodings
Computations in init
“Better to ask for fogiveness than for permission”

