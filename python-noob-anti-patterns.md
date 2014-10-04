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

# Using an index variable for iteration

    for (int i = 0; i < LENGTH; i++) {  // C, C++, C#, Java, JavaScript
        do_something(items[i])
    }

    for i range(len(items)):  # BAD
        do_something(items[i])

    for item in items:  # BETTER
        do_something(item)

# Getters

    public class Point {

        private Integer x;
        private Integer y;

        public void Point(Integer x, Integer y) {
            this.x = x;
            this.y = y;
        }

        public Integer getX() { return this.x; }
        public Integer getY() { return this.y; }
        public void setX(Integer x) { this.x = x; }
        public void setY(Integer y) { this.y = y; }
    }

    class Point(object):

        def __init__(self, x, y):
            self._x = x
            self._y = y

        def get_x(self):
            return self._x

        def get_y(self):
            return self._y

        def get_r(self):
            return math.sqrt(self._x ** 2 + self._y ** 2)

        def get_theta(self):
            return math.atan2(self._y, self._x)


    class Point(object):

        def __init__(self, x, y):
            self._r = math.sqrt(x ** 2 + y ** 2)
            self._theta = math.atan2(y, x)

        def get_x(self):
            return self._r * math.cos(self._theta)

        def get_y(self):
            return self._r * math.sin(self._theta)

        def get_r(self):
            return self._r

        def get_theta(self):
            return self._theta

    class Point(object):

        def __init__(self, x, y):
            self.x = x
            self.y = y

        @property
        def r(self):
            return math.sqrt(self.x ** 2 + self.y ** 2)

        @property
        def theta(self):
            return math.atan2(self.y, self.x)

    >>> point = Point(10, 20)
    >>> point.x, point.y, point.r, point.theta
    (10, 20, 22.360679774997898, 1.1071487177940904)


    class Point(object):

        def __init__(self, x, y):
            self.r = math.sqrt(x ** 2 + y ** 2)
            self.theta = math.atan2(y, x)

        @property
        def x(self):
            return self.r * math.cos(self.theta)

        @property
        def y(self):
            return self.r * math.sin(self.theta)

    >>> point = Point(10, 20)
    >>> point.x, point.y, point.r, point.theta
    (10.000000000000004, 20.0, 22.360679774997898, 1.1071487177940904)

    class Point(object):

        def __init__(self, x, y):
            self.r = math.sqrt(x ** 2 + y ** 2)
            self.theta = math.atan2(y, x)

        x = property(lambda self: self.r * math.cos(self.theta))
        y = property(lambda self: self.r * math.sin(self.theta))

# Setters

    class Point(object):

        def __init__(self, x, y):
            self.x = x
            self.y = y

        @property
        def r(self):
            return math.sqrt(self.x ** 2 + self.y ** 2)

        @property
        def theta(self):
            return math.atan2(self.y, self.x)

        @r.setter
        def r(self, r):
            theta = self.theta
            self.x = r * math.cos(theta)
            self.y = r * math.sin(theta)

        @theta.setter
        def theta(self, theta):
            r = self.r
            self.x = r * math.cos(theta)
            self.y = r * math.sin(theta)

    >>> point = Point(10, 20)
    >>> point.theta = 0
    >>> point.x, point.y, point.r, point.theta
    (22.360679774997898, 0.0, 22.360679774997898, 0.0)


# Mixing up class and instance variables

    public class Point {

        private Integer x;
        private Integer y;

        public void Point(Integer x, Integer y) {
            this.x = x;
            this.y = y;
        }
    }

    class Point(object):

        x = 0
        y = 0

        def __init__(self, x, y):
            self.x = x
            self.y = y

    >>> point = Point(10, 20)
    >>> point.x
    10
    >>> Point.x
    0

    class Point(object):

        def __init__(self, x, y):
            self.x = x
            self.y = y

    >>> point = Point(10, 20)
    >>> point.x
    10
    >>> Point.x
    AttributeError: type object 'Point' has no attribute 'x'

# Using `import *`

    # BAD
    from io import *
    from numpy import *
    file = open('./file.txt')

    # GOOD
    import io
    import numpy as np
    file = io.open('./file.txt')

    # AS GOOD
    from io import open
    file = open('./file.txt')

# Emulating end’s

    def some_function():
        other_function()
        yet_another_function()

        # end


    def some_function():
        other_function()
        yet_another_function()

        return


# If-else instead of dictionary look-ups

    # BAD
    def parse_currency(source):
        if source == '$':
            return 'USD'
        elif source == '€':
            return 'EUR'
        elif source == '¥':
            return 'JPY'
        elif source == '£':
            return 'GBP'

    # GOOD
    def parse_currency(source):
        currencies = {'$': 'USD', '€': 'EUR', '¥': 'JPY', '£': 'GBP'}
        return currencies[source]

    # GOOD
    {'$': 'USD', '€': 'EUR', '¥': 'JPY', '£': 'GBP'}[source]



Not using static analysis tools
------------------------------------------------------------
    Not using pyflakes
        Unused variables, imports
    Not following PEP 8
        Long lines

    flake 8

    Vim, Emacs, Sublime Text, PyCharm

Documentation
------------------------------------------------------------

# Comments instead of docstrings


    # This funciton does this and that
    def some_function(some_argument):
        ...

    def some_function(some_argument):
        """This function does this and that."""


# Docstrings in wrong places

    # BAD
    import io
    """This module does this and that."""

    # GOOD
    """This module does this and that."""
    import io

# Using JavaDoc/NDoc coventions

    def __init__(name, age)
        """
        <summary>
          Employee Class constructor
          <code>
            employee = Employee('dhaval', 25)
          </code>
        </summary>
        <param name="name">Name of the employee</param>
        <param name="age">Age of the employee</param>
        """
        ...


    """Parse command line arguments.

    Parameters
    ----------
    doc : str
        Description of your command-line interface.
    argv : list of str, optional
        Argument vector to be parsed. sys.argv[1:] is used
        if not provided.

    Returns
    -------
    args : dict
        A dictionary, where keys are names of command-line
        elements such as e.g. "--verbose" and "<path>", and
        values are the parsed values of those elements.

    """

    PEP 257: general docstring conventions
    pep257: tool for enforcing PEP 257

    NumPy / Sphinx: specific docstring conventions

# Excessive commenting

    # Increment variable i
    i = i + 1

    # BAD
    # If `grid` is square
    if set(map(len, grid)) == {len(grid)}:
        ...

    # BEST
    @property
    def is_square(self):
        return set(map(len, grid)) == {len(grid)}

    if grid.is_square:
        ...



# Unrepeatable doctests

    >>> Tweet(id=513015579687403520).sentiment
    'angry'

    >>> Tweet(text='OMG SO AWESOME').sentiment
    'happy'

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

Shell scription
------------------------------------------------------------

# Wrong or no shebang

    # BAD
    #! /macports/bin/python
    #! /usr/bin/python

    # GOOD
    #! /usr/bin/env python
    #! /usr/bin/env python2
    #! /usr/bin/env python3

# Not printing to `stderr` on error
# Not returning exit-codes on error

    import sys

    if not authorization.is_valid:
        sys.stderr.write('You are not authorized.')
        sys.exit(1)


# Manually parsing `sys.argv`

   Use docopt/argparse/optparse or something else.


Exceptions
------------------------------------------------------------

# Catch-all try-except blocks... pass

    try:
        do_something()
    except SomeError:
        pass

# Catching exception and rasing a different one

    try:
        import numpy
    except ImportError:
        raise Exception('You need NumPy installed')

# Putting a lot of code inside try-except

    # BAD
    try:
        one = foo()
        two = bar(one)
        result = baz(two)
    except KeyError:
        result = some_fallback()


    # GOOD
    try:
        one = foo()
    except KeyError:
        result = some_fallback()
    else:
        two = Bar(one)
        result = Baz(two)



Not knowing built-ins (also len)
------------------------------------------------------------


# Using `sorted` instead of `min` or `max`

    max_value = sorted(all_values)[-1]  # BAD
    max_value = max(all_values)         # GOOD

# Doing `list(reversed(sorted(...)))`

    reversed(sorted(collection))       # BAD
    sorted(collection, reversed=True)  # GOOD

# `try-except: KeyError` instead of `get`

    # BAD
    try:
        value = dictionary[key]
    except KeyError:
        value = DEFAULT_VALUE

    # GOOD
    value = dictionary.get(key, DEFAULT_VALUE)




Not knowing standard library
------------------------------------------------------------
# Not knowing about `collections.Counter` (or `nltk.FreqDist`)

    >>> from collections import Counter
    >>> Counter(['A', 'A', 'B', 'A', 'C', 'D', 'D'])
    Counter({'A': 3, 'D': 2, 'C': 1, 'B': 1})

# Using `randint` instead of other alternatives (off-by-one often)

    item = items[random.randint(0, len(items))]  # BAD

    item = random.choice(items)  # GOOD

# Overuse of `copy` and `deepcopy`
    ???

Other
-----

# Reinventing special methods (write, delete)
# Functions and methods for printing objects

   class Point(object):

       def __init__(self, x, y):
           self.x, self.y = x, y

       # BAD
       def to_string(self):
           return '({} . {})'.format(x, y)

       # GOOD
       def __str__(self):
           return '({} . {})'.format(x, y)

# Guided to Python special methods:
http://www.rafekettler.com/magicmethods.html

# Using magic methods directly

    items.__contains__(item)  # BAD

    item in items             # GOOD

# Printing instead of returning a value

    def analyse_sentiment(text):
        ...
        print result

    def analyse_sentiment(text):
        ...
        return result

Weird anti-patterns: `for _ in range(1): ... break`
Local imports
Not using context-managers, list-comprehensions
Messing up encodings
Computations in init
“Better to ask for fogiveness than for permission”
