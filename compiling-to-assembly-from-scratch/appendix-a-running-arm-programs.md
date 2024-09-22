---
title: "Appendix A: Running ARM Programs • Compiling to Assembly from Scratch"
---

```{=html}
<h1>Compiling to Assembly<small><small><br/>from Scratch</small></small><br/></h1>
<center><p> — <a href='./#table-of-contents'>Table of Contents</a> — </p></center>
<span id="fold"> </span>
<h1><br/><small><small>Appendix A</small></small><br/>Running ARM Programs<br/><br/></h1>
```

<!-- Changes chapter labels from "Chapter" to "Appendix" -->
\titleformat{\chapter}[display]{\bfseries\centering}{\huge Appendix \thechapter}{1em}{\Huge #1}

\appendices

\chapter{Running ARM Programs}

## 32-bit Linux on ARM (e.g. Raspberry Pi)

If you're a lucky owner of an ARM board like Raspberry Pi, you don't need any special steps.
You can use the built-in `gcc` toolchain and run the produced executables natively, as discussed in the book.
Just make sure to run a 32-bit operating system.

For example, assuming you have an assembly listing `hello.s` from *Part I*, you can assemble it like this:

```sh
$ gcc hello.s -o hello
```

And then, you can run the produced executable natively:

```sh
$ ./hello
Hello, assembly!
```

Even though modern Raspberry Pi boards have a 64-bit–capable processor, they can perfectly well run 32-bit operating systems.

If you want to run a 64-bit OS on Raspberry Pi, you can still execute 32-bit code.
In that case the instructions that follow apply.

## 64-bit Linux on ARM

The following instructions are relevant in case you're running 64-bit Linux on an ARM device, for example:

 * a newer Raspberry Pi,
 * an ARM laptop, such as Pinebook Pro,
 * an ARM development board,
 * an ARM server or compute instance.

The good news is that most 64-bit ARM processors are backwards-compatible and can run 32-bit ARM executables natively.

> **Well, actually…**
> 
> There are cases when chip manufactures disable 32-bit support to save costs.
> Most notably, this is the case for Apple Silicon.

Note, in the case of 64-bit Linux on ARM, the built-in `gcc` toolchain supports only the 64-bit version of ARM assembly, which is different from the 32-bit assembly used in this book.
That means you need to install a version of the `gcc` toolchain that targets 32-bit ARM.
Assuming a Debian-based Linux distro with `apt-get` package manager, you can install it as follows:

```sh
$ sudo apt-get install gcc-arm-linux-gnueabihf
```

Now, whenever the book uses `gcc`, you need to use `arm-linux-gnueabihf-gcc -static` instead.
For example, assuming you have an assembly listing `hello.s` from *Part I*, you can assemble it like this:

```sh
$ arm-linux-gnueabihf-gcc -static hello.s -o hello
```

But then, you can run the produced executable natively:

```sh
$ ./hello
Hello, assembly!
```

## Linux on x86-64 using QEMU

This guide assumes that you don't have access to an ARM Linux machine like a Raspberry Pi or a Pinebook Pro, but only to a good old x86-64 computer based on an AMD or Intel processor.

> The following has been tested on Ubuntu 20.04 LTS, but it should work the same on all Debian-based Linux distros.
> For other distros, you might need to use a different package manager.
> The package names could be slightly different, as well.

On an x86-64 Linux machine, the default `gcc` toolchain expects x86-64 assembly, which is quite different from the 32-bit assembly described in this book.
That means you need to install a version of the `gcc` toolchain that targets 32-bit ARM.
Assuming a Debian-based Linux distro with `apt-get` package manager, you can install it as follows:

```sh
$ sudo apt-get install gcc-arm-linux-gnueabihf
```

Now, whenever the book uses `gcc`, you need to use `arm-linux-gnueabihf-gcc -static` instead.
For example, assuming you have an assembly listing `hello.s` from *Part I*, you can assemble it like this:

```sh
$ arm-linux-gnueabihf-gcc -static hello.s -o hello
```

However, you can't just run this executable because it is made for an ARM processor:

```sh
$ ./hello
-bash: ./hello: cannot execute binary file: Exec form…
```

To run it, we need to install QEMU—a piece of software that allows emulating different processors, including ARM.
There are several ways to use it.
The `qemu-user` package enables emulation for individual executables, instead of emulating the whole operating system.

```sh
$ sudo apt-get install qemu-user
```

Now, the next step is no mistake:

```sh
$ ./hello
Hello, assembly!
```

What just happened?
How are we running an ARM binary on x86-64?
It turns out `qemu-user` has a smart mechanism: when installed, it configures itself to handle ARM binary files (which is not unlike how we can run shell scripts as if they were binaries).
However, on some Linux configurations, this won't work, and you need to be a little bit more explicit about invoking QEMU:

```sh
$ qemu-arm ./hello
Hello, assembly!
```

Note that even though the package name is `qemu-user`, the executable name that we're interested in is `qemu-arm`, since ARM is one of several possible target of QEMU.

## Windows on x86-64 using WSL and QEMU

Follow the steps to enable Windows Subsystem for Linux (WSL).
Ubuntu 20.04 LTS has been tested for this purpose.

*<https://ubuntu.com/wsl>*

Now, open a WSL terminal and follow the steps described in the previous section, *Linux on x86-64 using QEMU*.


