---
title: "AI=true is an Anti-Pattern
fancy-title: "<big>AI=true</big><br/><small>is an Anti-Pattern</small>"
date: 2026-02-25
#cta: {book: false}
---

One programming trend that surpised me a lot recently, something that happens both at work and in open-source, is people *suddenly* starting doing the following:

* Writing a lot of relevant, long-overdue, sharp, concise, to-the-point documentation… but placing it in `copilot-instructions.md` or `AGENTS.md` files.
* Implementing extremely valuable workflows, but exposing them in form of `skills` or <abbr title="Model Context Protocol">MCP</abbr> servers.
* Improving output of tests and command-line tools, but enabling it only under AI-oriented flags and environmental variables (like `AI=true`).

Well, I think we need to take deep breath and take a step back.

## Documentation

Yes, good documentation *is* valuable for AI agents, especially if it is not part of the training data set. A good documentation *digest* is often even more important, because it takes less of the context window. But… that documentation is equally valuable for humans, and we have a limited context window too, and benefit from good summaries equally. 

Moreover, we should strive to place the documentation where it is well discoverable by both humans and AI agents. `README.md` files is one such choice.

I know that there are a few technicalities involved, for example, some tools will pre-load files like `AGENTS.md` into the context, but the actual conventions are changing rapidly, and often are vendor-specific (i.e. not to be relied upon), and most of the benefit can be obtained by placing "See `README.md`" in the right place.

## Tools

First, there are tools that are mostly human-oriented, tools with graphical user interfaces. Then there are new kinds of tools that are primarily AI-oriented, the MCP tools. However, there's a set of tools that both developers and AI agents can use alike: command-line tools and APIs. They are scriptable, composable, text-oriented, and can perfectly expose functionality to both developers and AI agents. Why not default to them?

I'm obviously biased towards command-line, but I use my share of GUI tools too. However, when it comes to MCP, I am yet to see a single case when it is supperior to a command-line tool. Maybe the time will prove me wrong.

One example: I've seen an MCP tool being introduced because the actual command-line tool took a lot of time to execute, was producing no output and was—bacause of that—often mistakingly terminated early by the agent. That reminds me of someone else who is also prone to that… I am! Well, who else, when running a new tool and presented with a hanging command-line, doesn't just Ctrl-C out of it, if nothing happens for straight 10 seconds?

Or the opposite—who is not overwhelmed when a tool produces tons of unnecessary output? I am. And same thing, it makes AI context window slide and leave out potentially more useful information. Mental overload, anyone?

Who likes it when tests execute fast and, if they fail, produce output that allows to easily narrow down the problem? You get the idea… What's good for the goose is good for the gander.

Making a new internal tool? Why not make a web app… and see developers always complain about missing functionality while you try to manage scope creep. Or make an API first. Even better, wrap it into a command-line too and see developers and AI agents alike mixing, matching, scripting away, and automating the workflows you would have never imagined, and being on top of their needs.

## Let's sum it up

1. Place documentation where both human developers and AI agents can expect it. For example, in `README.md`, not `AGENTS.md`.
2. Prefer exposing functionality as command-line tools and APIs, which are well accessible to developers and AI agents alike, over GUI and MCP tools.
3. Avoid parameters (command-line, environment, etc.) that segregate workflows between humans and AI agents, for example, avoid `AI=true`, prefer `--quiet` or—*even better!*—design your tools with limited context/mental-overload in mind.
4. In general, avoid making workflows that are available to AI but hard to access for humans, and vice-versa.

* * *

I don't normally write on topics like this, but this has been my cry to try to turn the tide of programming practice towards unification of human and AI workflows.

There's enough similarity between us to maintain the same textual interfaces and conventions. We should try to stay interoperable as far as possible, but the ramifications are not lost on me.

