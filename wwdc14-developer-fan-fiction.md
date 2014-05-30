WWDC14 Developer Fan Fiction
============================

<center>30-05-2014</center>

When Apple unveiled their WWDC14 slogan
“Write the code. Change the world.”
everyone focused on the “Change the world” part and
assumed that Apple is entering the home
automation market. Now, after the WWDC is over,
we know that the key part was “Write the code”.

<center><img src='/wwdc14.jpg'></center>

It seems like this WWDC was a disappointment for consumers.
Major predictions, iWatch and a thinner 12-inch
MacBook Air did not confirm.
Minor stuff:
Air becoming more power efficient and cheaper, iPad Air
getting the fingerprint scanner. The new “best OSX and
iOS we’ve ever made” and so on.
Everyone expects a new category-defining product
from Apple, but instead we got iterations of
existing products.

However, developers still don't know what to think
of the “Objective”. Craig Federighi presented it
very quickly, without particular emphasis.
It will first be available in
Xcode 6.0 “later this Autumn”. It is still not clear,
whether it is a replacement for Apple Script, Automator,
or Objective-C.

Example
-------

Here is the hello-world example, transcribed from the
keynote slides.

First, the Objective-C version:

    #import "AppDelegate.h"


    @implementation AppDelegate

    - (BOOL)application:(UIApplication *)application
    didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
    {
       id _alert = [[UIAlertView alloc]
                           initWithTitle: @"Hello"
                           message: @"Hello from Objective"
                           delegate: nil
                           cancelButtonTitle: @"OK"
                           otherButtonTitles: nil];
       [_alert show];

       return YES;
    }

    @end

And now, the “Objective” version:

    import AppDelegate


    implementation AppDelegate

     - application: app didFinishLaunchingWithOptions: options

       _alert = UIAlertView alloc initWithTitle: "Hello"
                                  message: "Hello from Objective"
                                  delegate: nil
                                  cancelButtonTitle: "OK"
                                  otherButtonTitles: nil
       _alert show

       ^ yes

    end

This seems to be readable for anyone who knows a little
bit of Objective-C.

Typing
------

One thing is clear: there are no type annotations.  As
Federighi mentioned, every object is assumed to be of
type `id` in Objective-C sense.

Syntax
------

- All literals as well as special syntax dropped the
  `@`-prefix.

- Statement separators (`;`) are now optional, like in
  other mainstream scripting languages.

- There are no braces to delimit methods, so it is not
  entirely clear if the code is indentation sensitive (like
  in Python programming language) or not.

- New `^`-syntax is introduced as a shortcut for `return`.

- It is a known Objective-C convention to prepend instance
  variables with underscore. In Objective this convention
  is taken to the next level and now every variable
  that starts with a single underscore is promoted to an
  instance variable. This allows to avoid explicit
  declaration of instance variables.

Header files
------------

- Header files are optional. You can still use the usual
  `.h` files together with the new `.obj` files, however
  it is only useful if you want to distribute your code as
  binary.

Memory management
-----------------

On Mac there will be an option between Automatic Reference
Counting (ARC) *with* and *without* cycle resolution. On iOS
the only option is *without*.

Performance
-----------

It is said that there is no performance penalty (assuming
cycle resulution is turned *off*), as long as you are using
Objective-C APIs and not C or C++ APIs.

Discussion
----------

Right now Objective does not seem like a radical change
comparing to its C-counterpart, only a syntactic one.
However, it could help Apple attract more developers
from the mainstream dynamic languages camp. Even more likely, it
is just a first shy step towards improving the language
for Apple’s platforms.

Apple is trying to clean-up the language
by removing the “C” from Objective-C. Many developers
already use what is commonly known as the `id`
subset of Objective-C (one where you use `id` for
all the types), and Apple is only formalizing and
promoting this subset by providing a more appropriate
syntax for it.

As you probably know, Objective-C is the child of
Smalltalk and C programming languages. By removing
“C” from Objective-C, Apple is effectively created
a new Smalltalk dialect.  However, it is
doubtfull that Apple will be bold enough to bring
more advanced features of Smalltalk, such as
Smalltalk code-browser, persisting a running system
in an image, or continuations.

Related languages
-----------------

There is a bit of controversy regarding the name
“Objective”. As it turns out, there already exists
a language called [Objective-Smalltalk](http://objective.st/).
This situation reminds of a Google [Go language issue](https://code.google.com/p/go/issues/detail?id=9).

Also, it is impossible not to mentioned another
two projects that allow you to write software for
Apple’s platforms in a Smalltalk-related languages:
[F-Script](http://www.fscript.org/) and
[RubyMotion](http://www.rubymotion.com/).

Summary
-------

Time will tell us whether Objective is going to be Apple’s new
flagship programming language, or if it is going to be
a short-lived experiment like [MacRuby](http://www.macruby.org/).
In any way, I am extremely excited to see a Smalltalk
dialect introduced and promoted by Apple.

Amazing how it all went full circle: from Steve Jobs
being introduced to the Smalltalk-80 system at Xerox PARC,
to NeXT betting on Objective-C, then Apple evolving
it by re-introducing blocks from Smalltalk, and
now introducing Objective, which is
indistinguishable from Smalltalk. [&#9991;](/ "Home")

<center>&#8258;</center>

<center markdown="1">
*Follow me on [Twitter](http://twitter.com/keleshev)*
</center>


