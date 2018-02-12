YAML: Quick Introduction
========================

**YAML** /'ya-mel/ *YAML Ain't Markup Language*

Simple data
-----------

YAML is "data serialization" language that matches your expectations about
data. Say, what do you expect the following to be?

    Quick brown fox jumped over the lazy dog.

Odds are you will say it is a string. Let's find out what YAML thinks about it:

    >>> yaml.load('Quick brown fox jumped over the lazy dog.')
    'Quick brown fox jumped over the lazy dog.'

Well, what about this one?

    3.1415926536

YAML agrees, it is a floating point number:

    >>> yaml.load('3.1415926536')
    3.1415926536

But that was trivial, right? What do you think of that:

    2011-11-18

That looks like a date to me and to YAML:

    >>> yaml.load('2011-11-18')
    datetime.date(2011, 11, 18)

Time also can be incorporated:

    >>> yaml.load('2011-11-18 19:00:59')
    datetime.datetime(2011, 11, 18, 19, 00, 59)

Data structures
---------------

What do you think is this:

    - eggs
    - ham
    - spam
    - French basil salmon terrine

For me it is a list of food. For YAML it is a list of strings:

    >>> yaml.load('''
        - eggs
        - ham
        - spam
        - French basil salmon terrine
        ''')
    ['eggs', 'ham', 'spam', 'French basil salmon terrine']

Unfortunately, YAML does not know concept of food, but it did well with list
of strings, I think.

Also, if you want a list to be in-line, add brackets around:

    >>> yaml.load('[eggs, ham, spam]')
    ['eggs', 'ham', 'spam']

Another one:

    registry: USS Enterprise (XCV 330)
    service: circa 2130s
    captain: unknown

Let's try it out:

    >>> yaml.load('''
        registry: USS Enterprise (XCV 330)
        service: circa 2130s
        captain: unknown
        ''')
    {'captain': 'unknown', 'registry': 'USS Enterprise (XCV 330)',
    'service': 'circa 2130s'}

There's a different terminology about this one, but I bet you'll agree that
this is *associative array* or *hash table* or *dictionary*. YAML calls it a
*mapping*.

More complex data structures
----------------------------

In dynamic languages like Perl, Ruby, JavaScript, and Python, where
objects are implemented as hash tables, you can convert easily YAML mappings
to objects:

    >>> class SpaceShip(object):
            pass

    >>> ship = SpaceShip()

    >>> ship.__dict__ = yaml.load('''
        registry: USS Enterprise (XCV 330)
        service: circa 2130s
        captain: unknown
        ''')

    >>> ship.registry
    'USS Enterprise (XCV 330)'

Also, you can have lists of lists, lists of mappings, mappings of mappings,
and so on:

    # file exmpl1.yaml
    foods:
      - eggs
      - pizza
    drinks:
      - water
      - vodka

    >>> yaml.load(open('exmpl1.yaml'))
    {'foods': ['eggs', 'pizza'], 'drinks': ['water', 'vodka']}

    # file exmpl2.yaml
    status:
      engine: on
      translocator: off
    misc:
      airbag installed: yes
      maintenance passed: no

    >>> yaml.load(open('exmpl2.yaml'))
    {'status': {'engine': True, 'translocator': False},
    'misc': {'maintenance passed': False, 'airbag installed': True}}

YAML uses indentation to distinguish data hierarchy, and uses it very flexibly:
you can have as little as 1 space to depict indent.

The above examples remind me to tell you about comments syntax (hash sign
`#` in YAML) and about boolean data in YAML:

    >>> yaml.load('[yes, Yes, YES, on, On, ON, true, True, TRUE]')
    [True, True, True, True, True, True, True, True, True]

    >>> yaml.load('[no, No, NO, off, Off, OFF, false, False, FALSE]')
    [False, False, False, False, False, False, False, False, False]

As you can see YAML has a very broad understanding of truthness and falseness.

Finally
-------

I think, I only scratched the surface of YAML awesomness, so if you have a
usecase which was not covered here, you are very likely to find one on the
official site [yaml.org](http://yaml.org), which you should check out anyway!

What's with XML?
----------------

You can continue using it. [&#9632;](/ "Home")
