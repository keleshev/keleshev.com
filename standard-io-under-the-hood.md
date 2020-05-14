---
title: Standard IO: Under the Hood
---


<style> #home { position:absolute; line-height: inherit; }
pre { margin-bottom: 0 }
small + p { margin-top: 0}
</style>

<span id=home><a title=Home href=/>☰</a></span>

<h1>
  Standard IO
<br/>
  <small><small>Under the Hood</small></small><br/>
</h1>

<center>2020-05-14</center>

What happens when you call `console.log` or similar in your language of choice?

Those are usually language primitives implemented in C or C++. Let's use V8 as an example, the JavaScript runtime written in C++ that powers Chrome and Node.js.

It will first call a utility funciton `WriteToFile`:

<small style=line-height:1.5> <small>
```cpp
void D8Console::Log(const debug::ConsoleCallArguments& args,
                    const v8::debug::ConsoleContext&) {
  WriteToFile(nullptr, stdout, isolate_, args);
}
```
<https://github.com/v8/v8/blob/4b9b23521e/src/d8-console.cc#L52-L55> </small> </small>

Which in turn, after preprocessing the JavaScript values will eventually call `fwrite`.


<small style=line-height:1.5>
<small>
```cpp
void WriteToFile(const char* prefix, FILE* file, Isolate* isolate,
                 const debug::ConsoleCallArguments& args) {
  if (prefix) fprintf(file, "%s: "&#8288;, prefix);
  for (int i = 0; i < args.Length(); i++) {
    HandleScope handle_scope(isolate);
    if (i > 0) fprintf(file, " ");

    Local<Value> arg = args[i];
    Local<String> str_obj;

    if (arg->IsSymbol()) arg = Local<Symbol>::Cast(arg)->Name();
    if (!arg->ToString(isolate->GetCurrentContext()).ToLocal(&str_obj)) return;

    v8::String::Utf8Value str(isolate, str_obj);
<div style='margin-left: -1.20em; background: lightgrey'>      int n = static_cast&lt;int>(fwrite(*str, sizeof(**str), str.length(), file));
</div>
    if (n != str.length()) {
      printf("Error in fwrite\n");
      base::OS::ExitProcess(1);
    }
  }
  fprintf(file, "\n");
}
```
<https://github.com/v8/v8/blob/4b9b23521e/src/d8-console.cc#L26>
</small>
</small>

The function `fwrite` is part of the C standard library, also known as *libc*.
There are several libc implementations on different platforms. On Linux the popular ones are *glibc* and *musl*.
Let's take musl.
There, `fwrite` is implemented in C as following:

<small style=line-height:1.5>
<small>
```c
size_t fwrite(const void *restrict src, size_t size, size_t nmemb, FILE *restrict f)
{
	size_t k, l = size*nmemb;
	if (!size) nmemb = 0;
	FLOCK(f);
	k = __fwritex(src, l, f);
	FUNLOCK(f);
	return k==l ? nmemb : k/size;
}
```
<https://github.com/bminor/musl/blob/05ac345f89/src/stdio/fwrite.c#L28-L36>
</small>
</small>

After a bit of indirection, this will call
a utility function `__stdio_write`, which will then make an (operating) *system call* `writev`.

<small style=line-height:1.5>
<small>
```c
size_t __stdio_write(FILE *f, const unsigned char *buf, size_t len)
{
	struct iovec iovs[2] = {
		{ .iov_base = f->wbase, .iov_len = f->wpos-f->wbase },
		{ .iov_base = (void *)buf, .iov_len = len }
	};
	struct iovec *iov = iovs;
	size_t rem = iov[0].iov_len + iov[1].iov_len;
	int iovcnt = 2;
	ssize_t cnt;
	for (;;) {
<div style='margin-left: -1.20em; background: lightgrey'>          cnt = syscall(SYS_writev, f->fd, iov, iovcnt);</div>
        /* … */
	}
}
```
<https://github.com/bminor/musl/blob/05ac345f89/src/stdio/__stdio_write.c#L15>
</small>
</small>

The `syscall` symbol here is a macro, which after some serious preprocessor hackery, will expand to `__syscall3`.

System calls differ between operating systems, and the way to perform them differs between processor architectures.
It usually requires to write (or generate) a bit of assembly.
On x86-64 musl defines `__syscall3` as following:

<small style=line-height:1.5>
<small>
```c
static __inline long __syscall3(long n, long a1, long a2, long a3)
{
	unsigned long ret;
	__asm__ __volatile__ ("syscall" : "=a"(ret) : "a"(n), "D"(a1), "S"(a2),
						  "d"(a3) : "rcx"&#8288;, "r11"&#8288;, "memory");
	return ret;
}
```
<https://github.com/bminor/musl/blob/593caa4563/arch/x86_64/syscall_arch.h#L26-L32>
</small>
</small>

This sets up the system call number and arguments.
On x86-64 the instruction for making system calls is called `syscall`.

After the syscall is made, the control transfers to the (Linux, in this case) kernel. But that's a whole 'nother story…

<center>⁂</center>

This blog post was inspired by the answer I wrote on Quora:
[How does C/C++ io work under the hood?](
https://www.quora.com/How-does-C-C-io-work-under-the-hood-Is-it-possible-to-code-it-from-scratch-without-any-library/answer/Vladimir-Keleshev-1) [&#9632;](/ "Home")





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
