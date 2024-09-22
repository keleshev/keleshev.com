---
no-fleuron: true
title: "15. Garbage Collection • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Chapter 15</small></small><br/>Garbage Collection<br/><br/></h1>
```

\chapter{Garbage Collection}
\includegraphics{chapter-illustrations/15.png}
\newpage

So far, we have used `malloc` to allocate memory dynamically, but we have never released it back to the operating system.
You would need to call `free` to achieve that, otherwise your program's memory consumption will only grow.

When a programmer needs to deallocate memory manually, it's called *manual memory management*.
For some languages that might be appropriate.
However, most languages offer *automatic memory management* in the form of *garbage collection*.

> **Well, actually…**
>
> Garbage collection is one several approaches to automatic memory management.
> The others are *reference counting* and *region-based memory management*.
>

The easiest way to incorporate a garbage collector into your compiler is to use an off-the-shelf component, such as Boehm–Demers–Weiser garbage collector (or Boehm GC) which is available as a library.
You can link this library and replace all the calls to `malloc` with `GC_malloc` from Boehm GC, and you're done!

But you are here not for the easy answers, are you?
Right!
Then, let's implement a simple garbage collector from scratch.

## Cheney's algorithm

We will be implementing a garbage collection algorithm called Cheney's algorithm, named after Chris J. Cheney.
Here's a simplified description of it.
We will get to more details in the following sections.

At program startup, a large memory area is allocated (for example, using `malloc` from `libc`).
This area is referred to as a *semi-space*.
You will see why shortly.
Our existing use of `malloc` for allocating arrays is replaced with a new function, that we call `allocate`, which
places the allocations (also called *blocks*) one after another in the semi-space.
Once there's not enough memory in the semi-space for allocation, a function we call `collect` is run.
It allocates a new semi-space and copies there only *live* objects from the old semi-space.
The old semi-space is referred to as the *from-space*, and the new one is referred to as the *to-space*.
The objects are *live* if they are reachable (by pointers) from the so-called *roots*.
The *roots* are pointers that point to objects that we know we want to keep ahead of time.
Examples of such pointers are pointers on the stack and in global variables.
When all live objects are copied to the to-space, the from-space is discarded (for example, using `free`).

When we run out of space again, we `malloc` a new semi-space.
Now the old semi-space that used to be the to-space becomes the from-space, and the process repeats.

The first challenge is to figure out which objects are live.
The other challenge is that when we copy blocks their addresses change, and that means that we need to update all pointers that point to those objects.



## Allocation and collection

We will start by writing a custom allocator function that will replace our current use of `malloc`.
Instead of calling `malloc` for each allocation, we will allocate a larger memory region and then will allocate many arrays (or other objects) there.
Such a memory region is usually—confusingly—called a *heap*, but in the context of Cheney's algorithm, it is typically referred to as a *semi-space*.

When talking about garbage collectors, we call individual spans of memory *blocks*.
Our flat, non-resizable arrays are precisely one block each. Still, more complicated data structures (such as resizable arrays that we also talked about) could be implemented as several blocks connected with pointers.
In this chapter, we'll use the term *block*, even though for our simple language it is synonymous with an array.

At program startup, we allocate a large space using `malloc`.
We need to manage three pointers:

* The pointer returned by `malloc` that we will call *semi-space start*.
* The *allocation pointer* which points to the first word in a space that is not occupied by a block.
* The pointer to the end of the semi-space (which is *semi-space start* plus the size of the space) that we'll call *semi-space end*.

We can store these pointers in a `.data` section of our program.
We can also store one or two of them in call-preserved registers.

\newpage

![State of the program at startup](figures/gc-0.svg)

> **Note**
> 
> We haven't talked about using call-preserved registers this way, but they can be used to hold global variables.
> For example, we can reserve, say, `r10` to hold a particular global variable.
> We can agree that we won't use this register for anything else in our code generator.
> Foreign function will also keep it put, since it is a call-preserved register.
> Registers are a precious resource, but sometimes it makes sense to reserve one of them for something important.
> It is common to assign the *allocation pointer* to a register this way.
 
The start and end pointers will not change until we create a new space.
The allocation pointer, however, will change with each allocation.
It starts out pointing at the same address as the semi-space start, and with each allocation moves towards the semi-space end.

Now we can implement the `allocate` function.
When it is called (with a number of bytes to allocate), we check if the area between the allocation pointer and the space end is enough to hold it.
Then, we increment the allocation pointer by the requested number of bytes and return the previous value of the allocation pointer as the result.
In other words, with each allocation, we pack blocks one after another from semi-space start to semi-space end.

After several allocations, the state of our program may look like in the figure on the next page.

<!--

\begin{center}
    \vfill
        \textit{(This space is reserved for jelly stains)}
    \vfill
\end{center}
-->

\newpage

![The state of our program: stack and heap](figures/gc-1.svg)


Here, we have a stack with three frames allocated.
The frames are connected using frame pointers.
The frames contain several pointers to the blocks that were previously allocated in our semi-space.
Those blocks have pointers between them (for example, an array with a nested array).
The pointers may have cycles (an array element points to the array itself).
The non-pointer words (left blank) hold some scalar data like numbers or booleans (both on the stack and in the semi-space).

The blocks have their length as the first word (as we did with arrays).
We call such word in a block a *header*.
(Headers usually occupy one or two words and can contain more data, such as object type, for example.)
In the figure, we denote each header with a letter "`H`" and group the words in the same block using rounded corners, so we can see the length of the block.
From the figure, you can see that we have allocated five blocks with lengths two and three words.

\newpage

![The two semi-spaces and their pointers](figures/gc-2.svg)


Let's say that the program wants to allocate a block of four words now.
However, there's not enough space in the semi-space (from the allocation pointer to the end of the semi-space).
When the `allocate` function is running, this condition must trigger garbage collection.


We start by allocating a new semi-space called the *to-space*, while we refer to the old one as the *from-space*.
They are named that because blocks are copied *from* the from-space *to* the to-space during collection.
In the figure, you can see the two semi-spaces.
They both use three pointers: *start*, *allocation*, and *end* pointers.

We will walk down the stack, frame-by-frame, and look at each word in a frame: is it a pointer or not?
With our existing tagging scheme, we can easily distinguish pointers from scalars.
This process is called *scanning*, and we use the *scan pointer* to track where we are right now in the scanning process.

In the figure, you can see the *scan pointer* and the newly allocated *to-space*.


\newpage

![Scanninng the stack: first pointer](figures/gc-3.svg)

As we scan down the stack, we encounter our first pointer.
We copy the corresponding block to the to-space and bump the value of the to-space allocation pointer.
In the figure, you can see the two-word block copied to the to-space.
The pointer on the stack is updated to point to the new block.
(The previous value of the pointer is shown with a dashed line.)
We also update the same block in the from-space: we replace the header word with a so-called *forwarding pointer*, shown in grey.

If in future we encounter other pointers pointing to the block that we just moved, we will need to update them.
That's why we store the forwarding pointer in the old block that points to the new block.
It's like when you move to a new address and leave a memo at the old one that you have moved, so your mail can be forwarded.
When we reach a block, we can also distinguish whether it starts with the header (a number) or a forwarding pointer (a pointer) using our tagging scheme.
Of course, the block length is lost, but we won't need it for the old block.

<!--Since we allocated a block in the to-space, the allocation pointer is incremented by the size of the block.-->

\newpage

![Scanninng the stack: second pointer](figures/gc-4.svg)

In the same frame, we skip over one word which holds a scalar, and encounter another pointer.
By following that pointer, we discover that it starts with a forwarding pointer instead of a header.
You can recognize that it's the same block that we have just moved.
This time, we do not copy the block.
Instead, we update the value on the stack with the value of the forwarding pointer.

Stacks also hold values of the saved link registers.
We know that their location is next to the saved frame pointers and can ignore them.
Or, in our case, we don't need special handling for them: since link registers are not tagged, they will be interpreted as scalars and skipped anyway.

Another question is—how far down the stack should we go?
At some point, we'll need to stop.
At the start of the program, in `main`, we can allocate a zero word on the stack and point the frame pointer there.
This way, we can find out which is the last frame in our program and stop.
There are also ways to achieve that without frame pointers.

\newpage

![Scanninng the stack: third pointer](figures/gc-5.svg)


We move to the next (and last) frame and start scanning again.
We encounter our last pointer on the stack.
Same as before, we copy the pointed block from the from-space to the to-space and replace the old block's header with a forwarding pointer.
The forwarding pointer is in grey, and the old value of the pointer is shown with a dashed line.

We have scanned the whole stack, and we should do similarly with other roots, such as global variables and registers.
To scan registers, we can save them on the stack before scanning the stack.

However, we are not finished: there's a block in the to-space that points to another block in the from-space.

\newpage

![Scanninng the to-space: first pointer](figures/gc-6.svg)

Similarly to how we scanned the stack, we now start scanning the to-space by looking at one word at-a-time and checking if it's a pointer.
If it's a pointer to a header—we copy the block to the to-space.
If it's a pointer to a forwarding pointer, we update the pointer to that value.

<!--Now, we point the scan pointer to the start of the to-space and begin scanning it one word at-a-time.-->

As we scan, we encounter our first pointer.
We allocate the pointed block on the to-space, update the pointer to point to the newly allocated block, and store a forwarding pointer (grey) in the old block.

You can see that, as we continued scanning the to-space, it grew by one block, so now we have more scanning to do.

\newpage

![Scanninng the to-space: second pointer](figures/gc-7.svg)

As we scan the newly-copied block, we encounter another pointer.
It points to a block in the from-space that has a forwarding pointer, so we only update the pointer to the new value, without copying, since that block has already been copied.
Once we finish that, there are no more blocks to scan—we have completed the collection phase.

We can see that there are two blocks in the from-space (now highlighted grey) that were not copied.
That means they are garbage.
Now we can dispose the from-space (using `free`) and, finally, allocate that four-word block that we wanted to allocate in the very beginning, before the collection started.
The program may now resume.

In the last figure, you can see the state of the program after the collection has finished and the from-space has been deallocated.

\newpage

![The state of our program after collection](figures/gc-8.svg)


## Tagging

We have used tagging to distinguish between scalar values and pointers to blocks.
If we didn't use tagging, we could check if a word's numeric value is between the from-space start and the from-space end.
If it's within that range, we can conclude that the value is a pointer; if it's not—we treat it as a scalar.
This is not always precise: our program might deal with some numeric value that just happens to be in that range.
In this case, the algorithm might keep blocks in memory that are garbage.
This is usually not a problem, in practice.
Garbage collectors that are not *precise* are called *conservative*.
Boehm GC is an example of such collector.

\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}

## Headers

Our implementation stored block length in the first word of the block, the header, matching our array layout.
However, often headers hold additional data for the garbage collector.
For example, a tag in the header can mean that the whole block consists only of scalars and should be skipped by the collector to save time.
This is relevant, for example, for handling large strings.

Also, when pointer tagging is not used, each block (and frame) can hold a field with information about which word is a pointer and which one is not.
This could be done in the form of a bit map, with one bit per word.
In other words, the tagging bits can be moved from each word to a central location in a block.



## Discussion

In this example, our semi-spaces were only 16 words or 64 bytes.
In reality, we need to allocate a larger area, and the larger it is, the fewer times we will need to collect garbage.

Now that we had an in-depth overview of Cheney's algorithm let's discuss some of the properties of such garbage collector.

First, it offers fast allocation.
Most of the time, allocation only needs to check that there's enough space left, and increment the allocation pointer—that's it!
This can be implemented in a hand-full of instructions and can be made even faster if the allocation pointer is assigned a dedicated call-preserved register.
Compare this to `malloc` where a typical implementation needs to execute 50 to 200 instructions before returning.

Second, it's a *compacting* or *moving* collector.
After the collection phase, all the blocks are allocated one-after-another without holes or fragmentation.
This is good for data locality and cache performance.

But not everything is perfect with this algorithm.

It is a *stop-the-world*, *non-concurrent* collector.
When collection happens, the program is paused until the collection finishes.
In a concurrent collector, the collection happens a-little–at-a-time with each allocation, to avoid long pauses.

Another property of this algorithm is that during the collection, when both semi-spaces are allocated the amount of memory consumed is twice as high.

Our collector is also *non-generational*.

## Generational garbage collection

It is observed that new blocks often become garbage fast.
And then some blocks stay around for a long time.
We want to scan new blocks more frequently to reclaim memory and scan older blocks more rarely, since they are less likely to become garbage.
This can be achieved with *generational* collectors.

For example, a collector with two generations G0 and G1 may have two heaps or spaces: a smaller one for G0 and a larger one for G1.
Collections happen more frequently in G0 and more rarely in G1.
They can also use different algorithms.
All new objects are allocated in G0, and after G0 collection happens, the blocks that remained are copied to G1.

Cheney's algorithm is a good fit for G0 collectors because of fast allocation and because it is a moving collector.
In such generational collector, we would copy blocks into G1 heap, and not into another semi-space.

 * * *

<!--- TODO Wind down -->
And with this, our journey comes to an end.
We have learned about parser combinators and made a parser for our language; learned about ARM assembly to implement the code generator; dipped our toes into static and dynamic typing, and learned a grabage collection algorithm.

We hope that you've enjoyed the journey, and—who knows—maybe we'll see each other again!
<!--- TODO Wind down -->

\section{PUSH TOC ONE LINE DOWN}

\newpage

<!--\includegraphics{chapter-illustrations/1.png}--

\newpage
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}-->


<!-- # Transformations and Optimizations -->

<!-- # System Calls -->


```{=html}
<center style="height:122px; overflow: hidden; position:relative;">
  <a href="./"><img id="spike" style="position:relative" src=./spike.png width=256 height=260 /></a>
  <!--img id="spike-2" style="position:relative" src=./spike-2.png width=256 height=260 /-->
</center>
```

<!--
TODO Add:

    emit() {
      if (this.left instanceof Integer) {
        if (this.right instanceof Integer) {
          new Integer(this.left.value + this.right.value).emit();
        } else if (this.left.value < 256) {
          this.right.emit();
          emit(`add r0, r0, #${this.right.value}`);
        } else {
          this.right.emit();
          emit(`mov r1, r0`);
          this.left.emit();
          emit(`add r0, r0, r1`);
        }
      } else {
        this.right.emit();
        emit(`push {r0, ip}`);
        this.left.emit();
        emit(`pop {r1, ip}`);
        emit(`add r0, r0, r1`);
      }
    }
-->
