from parsimonious.grammar import Grammar


python2 = '''
and as assert break class continue def del elif else except exec
finally for from global if import in is lambda not or pass print
raise return try while with yield'''.split()

python3 = '''
False None True and as assert break class continue def del elif
else except finally for from global if import in is lambda
nonlocal not or pass raise return try while with yield'''.split()

ruby = '''private BEGIN END alias and begin break case class def defined?
do else elsif end ensure false for if module next nil not or redo
rescue retry return self super then true undef unless until when
while yield'''.split()

scala = '''abstract case catch def class do else extends false
final finally for forSome if implicit import lazy match new null
object override package private protected return sealed super
this throw trait try true type val var while with yield
_ : = => <- <: <% >: # @'''.split()

ocaml = '''let module struct end open in type of function
val sig match with fun try exception if then else true false rec
as'''.split()


class Highlighter(object):

    def __init__(self, keywords=python2):
        self.keywords = keywords

    def parse(self, source):
        grammar = '\n'.join(getattr(v, '__doc__') or '' for k, v in
                            vars(self.__class__).items() if '__' not in k)
        return Grammar(grammar)['top'].parse(source)

    def eval(self, source):
        node = self.parse(source) if isinstance(source, basestring) else source
        method = getattr(self, node.expr_name, lambda node, children: children)
        return method(node, [self.eval(n) for n in node])

    def top(self, node, children):
        '''top = (manual / string / attribute
               / word / symbol / comment / glyph / _ )+'''
        return ''.join(child[0] for child in children)

    def manual(self, node, children):
        r'manual = "!!!" ~".*?\n"'
        return node.text.lstrip('!')

    def string(self, node, children):
        '''string = ~"[a-z]"? ('"' ~'[^"]*' '"')'''
        text = node.text.replace('%d', '<b>%d</b>').replace('%s', '<b>%s</b>')
        return '<em>%s</em>' % text

    def other(self, node, children):
        'other = (!"#" ~"\W")+'
        return node.text

    def attribute(self, node, children):
        'attribute = "." ~"[a-zA-Z0-9_@$!=?\[\]]+"'
        return node.text

    def symbol(self, node, children):
        'symbol = ":" ~"[a-zA-Z0-9_@$!=?\[\]]+"'
        return '<em>%s</em>' % node.text

    def comment(self, node, children):
        r'comment = ("#" ~".*" "\n") / ("(*" ~".*?\*\)"s)'
        return '<em>%s</em>' % node.text

    def glyph(self, node, children):
        # r'''glyph = ~"[^'\s]"+'''
        r'''glyph = (!(~"\s" / '"' / word) ~".")+'''
        return node.text

    def word(self, node, children):
        'word = ~"\w+" ~"\s"*'
        text = node.text
        if text[0].isupper():
            return '%s' % text
        return text if text.rstrip() not in self.keywords else '<b>%s</b>' % text

    def _(self, node, children):
        '_ = ~"\s"+'
        return node.text
