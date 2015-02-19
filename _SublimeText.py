from dragonfly import *
import time

#Somehow redefining the context wasn't good enough, so that's
#why this file has "_" before its name
sublime_context = AppContext(title="sublime")
grammar = Grammar("Sublime", context=sublime_context)

class SublimeMappingRule(MappingRule):
    mapping={
        #sublime actions
        "save (file | document)" : Key("c-s"),
        "build (file | document)" : Key("c-b"),
        "go to (file | document)" : Key("c-p"),
        "go to (file | document) <text>" : Key("c-p") + Text("%(text)s"),

        # navigation move up down left right with or without words
        "go [<n>] [(lines|line)] down [<n>]" : Key("down:%(n)d"), # laag so la
        "go [<n>] [(lines|line)] up [<n>]" : Key("up:%(n)d"), # high, hoog but don't like hi or ho kind of hay and stop. so ha
        "go left [<n>]" : Key("left:%(n)d"), # left so le
        "go right [<n>]" : Key("right:%(n)d"), #right so ri.. or something
        "go [<n>] (words | word) left [<n>]" : Key("c-left:%(n)d"),
        "go [<n>] (words | word) right [<n>]" : Key("c-right:%(n)d"),

        # navigation select by moving up down left right with or without words
        "mark [<n>] [(lines|line)] down [<n>]" : Key("shift:down, down:%(n)d, shift:up"),
        "mark [<n>] [(lines|line)] up [<n>]" : Key("shift:down, up:%(n)d, shift:up"),
        "mark left [<n>]" : Key("shift:down, left:%(n)d, shift:up"),
        "mark right [<n>]" : Key("shift:down, right:%(n)d, shift:up"),
        "mark [<n>] (words | word) left [<n>]" : Key("shift:down, c-left:%(n)d, shift:up"),
        "mark [<n>] (words | word) right [<n>]" : Key("shift:down, c-right:%(n)d, shift:up"),

        "go to line" : Key("c-g"),
        "go to line <n>" : Key("c-g") + Text("%(n)d") + Key("enter"),

        "space <text>" : Key("space") + Text("%(text)s"),
        "[insert] text <text>" : Text("%(text)s"),
        
    }
    extras=[
            Integer("n", 1, 1000),
            Dictation("text"),
           ]
    defaults = {
                "n": 1,
               }


class LatexEditingRule(MappingRule):
    mapping={
        "new (chapter | section)": Text("\section{}") + Key("left"),
        "new subsection": Text("\subsection{}") + Key("left"),
        "(open | show) pdf" : Key("ctrl:down, l, o, ctrl:up")
    }
    extras=[
            Dictation("text"),
           ]


sublimeRule = SublimeMappingRule()
grammar.add_rule(sublimeRule)
latexRule = LatexEditingRule()
grammar.add_rule(latexRule)

grammar.load()
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None

