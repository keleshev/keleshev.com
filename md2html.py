#!/usr/bin/env python
import sys
from re import compile as re

from markdown2 import markdown

import hi
from iconize import icons


def add_youtube(source):
    pattern = r'''<iframe width="640" height="360"
                         src="//www.youtube.com/embed/\1?rel=0"
                         frameborder="0" allowfullscreen></iframe>'''
    return re('\((\S+?)@youtube\)').sub(pattern, source)

def add_hoverquotes(source):
    source = source.replace('".',
      '<span><span style="position: absolute">.</span>&rdquo;</span>')
    source = source.replace('",',
      '<span><span style="position: absolute">,</span>&rdquo;</span>')
    source = source.replace('."', '."<h6>Error: Use UK quotation style, not US</h6>')
    source = source.replace(',"', '."<h6>Error: Use UK quotation style, not US</h6>')
    return source

def add_negation(source):
    pattern = r'<span style="text-decoration: overline">\1</span>'
    pattern = r'<span style="display: inline-table; border-top: 1px solid black;">\1</span>'
    source = re('-\((.*?)\)').sub(pattern, source)
    return re('-\[(.*?)\]').sub(pattern, source)


def add_icons(source):
    def repl(match):
        icon_name = match.groups(1)[0]
        if icon_name not in icons:
            raise Exception('Icon "%s" is not found' % icon_name)
        icon = icons[icon_name]
        print icon, repr(icon)
        return '<i>%s</i>' % icon
    return re('i`(\w+)`').sub(repl, source)


def add_inline_code(source):
    def repl(match):
        code = match.groups(1)[0]
        return '<code>%s</code>' % code
    return re('`(.+?)`').sub(repl, source)


def parse_header(source):
    before, during, after = source.partition('===')
    return before.strip()


template = open('TEMPLATE.html').read().decode('utf-8')
code = re('(?s)```(\w+)\n(.*?)```')


def highlight(match):
    language, source = match.groups()
    highlighter = hi.Highlighter(getattr(hi, language))
    return u'<pre>%s</pre>' % \
        highlighter.eval(
source)


for file in sys.argv[1:]:
    new_file = file.partition('.md')[0] + '.html'
    print '%s -> %s' % (file, new_file)
    contents = open(file).read().decode('utf-8')
    contents = unicode(contents)
    header = parse_header(contents)
    contents = add_youtube(add_negation(add_icons(contents)))
    contents = add_hoverquotes(contents)
    contents = code.sub(highlight, contents)
    html = markdown(contents, extras=['smarty-pants', 'wiki-tables'])
    html = add_inline_code(html)

    html = template.replace('{{body}}', html)
    html = html.replace('{{title}}', header)
    open(new_file, 'w').write(html.encode('utf8'))
