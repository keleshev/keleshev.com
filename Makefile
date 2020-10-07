.PHONY: phony

SOURCES = $(shell find . -path ./docs -prune -false -o -name '*.md')
TARGETS = $(SOURCES:./%.md=docs/%.html)  # ./foo.md -> docs/foo.html

all: $(TARGETS)

docs/%.html: %.md template.html Makefile
	pandoc $< -o $@ --template=template.html --highlight-style=monochrome
