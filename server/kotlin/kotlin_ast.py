from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from server.kotlin.antlr.KotlinLexer import KotlinLexer
from server.kotlin.antlr.KotlinParser import KotlinParser


def get_ast(code):
    inp_stream = InputStream(code)
    lexer = KotlinLexer(inp_stream)
    lexer.removeErrorListeners()
    my_listener = MyErrorListener()
    lexer.addErrorListener(my_listener)
    stream = CommonTokenStream(lexer)
    parser = KotlinParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(my_listener)
    tree = parser.kotlinFile()
    # str_tree = Trees.toStringTree(tree, None, parser)
    # reg = re.compile(r'\s\(\s*\)')
    # sub = reg.sub('', str_tree)
    # sub = str_tree.replace('"', '\\"')
    # print(sub)
    # return get_dot(sub)
    my_tree = Ast()
    my_tree.gen_ast(tree, False, 0)
    my_tree.create_dot()
    res = my_tree.dot_tree
    if res == "digraph g {" or res == "digraph g {\n}":
        raise RuntimeError('Something wrong')
    return res


class Ast:
    def __init__(self):
        self.line_num = []
        self.type_rule = []
        self.content = []
        self.dot_tree = "digraph g {"

    def gen_ast(self, ctx, verbose, index):
        ignored = not verbose and ctx.getChildCount() == 1 and isinstance(ctx.getChild(0),
                                                                          ParserRuleContext)
        if not ignored:
            rule_name = KotlinLexer.ruleNames[ctx.getRuleIndex()]
            self.line_num.append(str(index))
            self.type_rule.append(rule_name)
            self.content.append(ctx.getText())  # full text of program
            # self.content.append(self.get_text(ctx))  # text of last nodes

        for i in range(ctx.getChildCount()):
            element = ctx.getChild(i)
            if isinstance(element, RuleContext):
                if ignored:
                    self.gen_ast(element, verbose, index)
                else:
                    self.gen_ast(element, verbose, index + 1)

    def create_dot(self):
        self.print_label()
        for i in range(1, len(self.line_num)):
            pos = self.get_pos(int(self.line_num[i]) - 1, i)
            self.dot_tree += "\n" + str(int(self.line_num[i]) - 1) + str(pos) + "->" + self.line_num[i] + str(i)
        self.dot_tree += "\n}"

    def print_label(self):
        for i in range(len(self.line_num)):
            self.dot_tree += "\n" + self.line_num[i] + str(i) + "[label=\"" + self.type_rule[i] + "\\n " + self.content[
                i].replace('"', '\\"') + " \"]"

    def get_pos(self, n, limit):
        pos = 0
        for i in range(limit):
            if int(self.line_num[i]) == n:
                pos = i
        return pos

    def get_text(self, node):
        if node.getChildCount() <= 1:
            return node.getText()
        else:
            return ""


class MyErrorListener(ErrorListener):

    def __init__(self):
        super(MyErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError("line: {}, column: {}, msg: {}, e: {}".format(line, column, msg, e))
