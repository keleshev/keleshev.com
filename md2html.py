#!/usr/bin/env python
import sys
from re import compile as re

from markdown2 import markdown

import hi


def add_youtube(source):
    pattern = r'''<iframe width="640" height="360"
                         src="//www.youtube.com/embed/\1?rel=0"
                         frameborder="0" allowfullscreen></iframe>'''
    return re('\((\S+?)@youtube\)').sub(pattern, source)


def add_negation(source):
    pattern = r'<span style="text-decoration: overline">\1</span>'
    pattern = r'<span style="display: inline-table; border-top: 1px solid black;">\1</span>'
    source = re('-\((.*?)\)').sub(pattern, source)
    return re('-\[(.*?)\]').sub(pattern, source)


def parse_header(source):
    before, during, after = source.partition('===')
    return before.strip()


template = open('TEMPLATE.html').read().decode('utf-8')
code = re('(?s)```(\w+)\n(.*?)```')


def highlight(match):
    language, source = match.groups()
    highlighter = hi.Highlighter(getattr(hi, language))
    return '<pre>%s</pre>' % highlighter.eval(str(source))


for file in sys.argv[1:]:
    new_file = file.partition('.md')[0] + '.html'
    print '%s -> %s' % (file, new_file)
    contents = open(file).read().decode('utf-8')
    header = parse_header(contents)
    contents = add_youtube(add_negation(contents))
    contents = code.sub(highlight, contents)

    html = markdown(contents, extras=['smarty-pants'])
    html = template.replace('{{body}}', html)
    html = html.replace('{{title}}', header)
    open(new_file, 'w').write(html.encode('utf8'))
