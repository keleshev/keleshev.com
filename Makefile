.PHONY: phony

SOURCES = $(shell find . -path ./docs -prune -false -o -name '*.md')
TARGETS = $(SOURCES:./%.md=docs/%.html)

REDIRECTS = $(shell find . -path ./docs -prune -false -o -name '*.redirect')
TARGETS += $(REDIRECTS:./%.redirect=docs/%.html)

FIGURES = $(shell find . -path ./docs -prune -false -o -name '*.svg')
TARGETS += $(FIGURES:./%.svg=docs/%.svg)

$(info $(TARGETS))

all: $(TARGETS)

publish: phony
	git push origin main

docs/%.html: %.md template.html Makefile
	mkdir -p $(@D)
	pandoc $< -o $@ --template=template.html --highlight-style=monochrome \
		-M document-css=false

docs/%.svg: %.svg Makefile
	mkdir -p $(@D)
	cp $< $@

docs/%.html: %.redirect Makefile REDIRECT.html
	mkdir -p $(@D)
	cat REDIRECT.html | sed s@{{TARGET}}@$$(cat $<)@g > $@
