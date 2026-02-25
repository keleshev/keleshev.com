---
title: "Say No to Human-AI Workflow Segregation"
fancy-title: "<big>Say No</big><br/><small>to Human-AI Workflow Segregation</small>"
date: 2026-02-25
#cta: {book: false}
---

One trend that surpised me a lot recently, something that happens both at work and in open-source, is people *suddenly* starting doing the following:

* Writing a lot of relevant, long-overdue, sharp, concise, to-the-point documentation… but placing it in `copilot-instructions.md` or `AGENTS.md` files.
* Implementing extremely valuable workflows, but exposing them in form of `skills` or <abbr title="Model Context Protocol">MCP</abbr> servers.
* Improving output of tests and other command-line tools, but hiding it under AI-oriented flags and environmental variables (like `AI=true`).

Well, I think we need a deep breath and take a step back.

Yes, good documentation *is* valuable for AI agents, especially if it is not part of the training data set. A good documentation *digest* is often even more important, because it takes less of the context window. But… that documentation is equally valuable for humans, and we have a limited context window too, and benefit from good summaries equally.

Next, tools. There are tools that are mostly human-oriented, tools with graphical user interfaces. Then there are new kinds of tools that are mostly AI-oriented, the MCP tools. However, there's a set of tools that both developers and AI agents prefer alike: command-line tools. They are scriptable, composable, text-only, and can perfectly expose functionality to both humans and AI agents. Why not focus on them?

I've seen a case where an MCP tool was introduced because the actual command-line tool took a lot of time to execute, was producing no output and was often terminated early by the agent. That reminds me of someone else who is also liable to that… I am! Well, who, when running a new tool and presented with a hanging command-line, doesn't just Ctrl-C out of it if nothing happens for 10 seconds?

Who is overwhelmed when a tool produces tons of unnecessary output? I am. And it makes AI context window slide and leave out potentially more useful information. Mental overload, anyone?

Who likes it when tests execute fast and, if they fail, produce output that allows to easily narrow down the problem? You get the idea…

## Summary

Let's sum it up in a few guidelines:

1. Place documentation where both human developers and AI agents can expect it. For example, in `README.md`, not `AGENTS.md`.
2. Prefer exposing functionality as command-line tools, which are equally well accessible to humans and AI agents, over GUI and MCP tools.
3. Avoid parameters (command-line, environment, etc.) that segregate workflows between humans and AI agents, e.g. avoid `AI=true`, prefer `--quiet` or, even better design your tools with context/mental-overload in mind.


I know that there are a few technicalities involved, for example, some tools will pre-load files like `AGENTS.md` into the context, but this actual conventions are changing rapidly, often vendor-specific (e.i. not to be relied upon), and most of the benefit can be obtained by placing "See `README.md`" in them.


* * *

It has become a cliché to say that LLMs are humanity's mirror: malleable, fallible, easy to fool, based on tech that mimics some of our tech, and shares a lot of training data with us. I think we should embrace the situation and try stay interoperable as long as possible, but the ramifications are not lost on me.



