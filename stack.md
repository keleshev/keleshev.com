The importance of being stackless <small>and optimizing tail calls</small>
=================================

A while ago I gave a talk called [Critique of Python](youtu.be/CpjUoYcaUu8).
I gave it on two occasions and had a lot of discussions afterwards.
One of the points of my critique was that Python is not
*stackless* and it doesn't optimize away *tail-calls*.
I didn't convince quite a lot
of people that these techniques are necessary.
And here I
want to expand on why I think they are essential.

What is *tail-call optimization*? <small>Skip this if you know</small>
--------------------

A function call is in a *tail position* if the result of the
call is used as the return value of the another function.

Here are some examples:

    def foo():
        tmp_1 = call_1()
        tmp_2 = call_1(tmp_1)
        return bar(tmp_2)  # Tail call.

    def foo():
        tmp = bar()  # Tail call,
        return tmp   # the value is returned immediately.

    def foo():
        tmp = bar()  # Not a tail call,
        tmp.x = 10   # the value is returned modified.
        return tmp

The interesting property of a
def foo(a):
    b = 2
    def bar(x):
        y = 4
        return inspect.stack()
    return bar(b)
