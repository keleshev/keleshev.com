from parsimonious.grammar import Grammar


python2 = '''
and as assert break class continue def del elif else except exec
finally for from global if import in is lambda not or pass print
raise return try while with yield'''.split()

python3 = '''
False None True and as assert break class continue def del elif
else except finally for from global if import in is lambda
nonlocal not or pass raise return try while with yield'''.split()


class Highlighter(object):

    def __init__(self, keywords=python2):
        self.keywords = keywords

    def parse(self, source):
        grammar = '\n'.join(getattr(v, '__doc__') or '' for k, v in
                            vars(self.__class__).items() if '__' not in k)
        return Grammar(grammar)['top'].parse(source)

    def eval(self, source):
        node = self.parse(source) if isinstance(source, str) else source
        method = getattr(self, node.expr_name, lambda node, children: children)
        return method(node, [self.eval(n) for n in node])

    def top(self, node, children):
        'top = (word / comment / _ / other)+'
        return ''.join(child[0] for child in children)

    def other(self, node, children):
        'other = (!"#" ~"\W")+'
        return node.text

    def comment(self, node, children):
        r'comment = "#" ~".*" "\n"'
        return '<i>%s</i>' % node.text

    def word(self, node, children):
        'word = ~"\w+" ~"\s"*'
        text = node.text
        return text if text.strip() not in self.keywords else '<b>%s</b>' % text

    def _(self, node, children):
        '_ = ~"\s"+'
        return node.text
