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
        "close tab" : Key("c-w"),

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

class SigleLetterRule(MappingRule):
    # Here we define this rule's spoken-form and special elements.
     
    mapping={
                "Alpha":     Text("a"),
                "Bravo":     Text("b"),
                "Charlie":   Text("c"),
                "Delta":     Text("d"),
                "Echo":      Text("e"),
                "Foxtrot":   Text("f"),
                "Golf":      Text("g"),
                "Hotel":     Text("h"),
                "India":     Text("i"),
                "Juliett":   Text("j"),
                "Kilo":      Text("k"),
                "Lima":      Text("l"),
                "Mike":      Text("m"),
                "November":  Text("n"),
                "Oscar":     Text("o"),
                "pope":      Text("p"),
                "Query":    Text("q"),
                "Romeo":     Text("r"),
                "Sierra":    Text("s"),
                "Tango":     Text("t"),
                "Uniform":   Text("u"),
                "Victor":    Text("v"),
                "Whiskey":   Text("w"),
                "X-ray":     Text("x"),
                "Yankee":    Text("y"),
                "Zulu":      Text("z"),
                "space":      Text(" "),
                "Big Alpha":     Text("A"),
                "Big Bravo":     Text("B"),
                "Big Charlie":   Text("C"),
                "Big Delta":     Text("D"),
                "Big Echo":      Text("E"),
                "Big Foxtrot":   Text("F"),
                "Big Golf":      Text("G"),
                "Big Hotel":     Text("H"),
                "Big India":     Text("I"),
                "Big Juliett":   Text("J"),
                "Big Kilo":      Text("K"),
                "Big Lima":      Text("L"),
                "Big Mike":      Text("M"),
                "Big November":  Text("N"),
                "Big Oscar":     Text("O"),
                "Big pope":      Text("P"),
                "Big Query":    Text("Q"),
                "Big Romeo":     Text("R"),
                "Big Sierra":    Text("S"),
                "Big Tango":     Text("T"),
                "Big Uniform":   Text("U"),
                "Big Victor":    Text("V"),
                "Big Whiskey":   Text("W"),
                "Big X-ray":     Text("X"),
                "Big Yankee":    Text("Y"),
                "Big Zulu":      Text("Z"),
                "slap" :         Key("enter"),
                "angle brackets": Key("langle"),
                "brackets": Key("lbracket"),
                "braces": Key("lbrace"),
                "parens": Key("lparen"),
                "quotes": Key("dquote"),
                "single quotes": Key("squote"),
                "backslash": Text("\\"),
               }

    extras=[
            Integer("n", 0, 1000),
            Dictation("text"),
            ]

class LatexEditingRule(MappingRule):
    mapping={
        "new (chapter | section)": Text("\section{}") + Key("left"),
        "new subsection": Text("\subsection{}") + Key("left"),
        "(open | show) pdf" : Key("ctrl:down, l, o, ctrl:up"),
        "bold": Text("b") + Key("tab"),
        "math equivalent":  Text("$\equiv$"),
        "big logic equivalent":  Text("$\Leftrightarrow$"),
        "logic equivalent":  Text("$\leftrightarrow$"),
        "implies":  Text("$\\rightarrow$"),
        "exists" : Text("$\exists$"),
        "for all" : Text("$\\forall$"),
        "in" : Text(" $\in$ "),
        "union" : Text(" $\cup$ "),
        "intersection" : Text(" $\cap$ "),
        "lower <n>" : Text("$_{%(n)d}$"),
        "lower" : Text("$_{}") + Key("left"),
        "open math" : Text("$"),
        "math sign" : Text("$\\"),
        "indent" : Text("\\begin{addmargin}{2em}")+Key("enter")+Text("\end{addmargin}")+ Key("up, end, enter"),

    }
    extras=[
            Integer("n", 0, 1000),
            ]

class PythonEditingRule(MappingRule):
    mapping={
        "run Python script": Key("a-t, s/10:2, right/10, p/10, right/10, up/10:2, enter")    
    }

#---------------------------------------------------------------------------
# Here we create an element which is the sequence of keystrokes.

# First we create an element that references the keystroke rule.
#  Note: when processing a recognition, the *value* of this element
#  will be the value of the referenced rule: an action.
alternatives = []
alternatives.append(RuleRef(rule=SublimeMappingRule()))
alternatives.append(RuleRef(rule=LatexEditingRule()))
alternatives.append(RuleRef(rule=PythonEditingRule()))
alternatives.append(RuleRef(rule=SigleLetterRule()))
single_action = Alternative(alternatives)
sequence = Repetition(single_action, min=1, max=16, name="sequence")

class SequenceRule(CompoundRule):
    # Here we define this rule's spoken-form and special elements.
    spec     = "<sequence>"
    
    extras   = [
                sequence,                 # Sequence of actions defined above.
               ]

    # This method gets called when this rule is recognized.
    # Arguments:
    #  - node -- root node of the recognition parse tree.
    #  - extras -- dict of the "extras" special elements:
    #     . extras["sequence"] gives the sequence of actions.
    #     . extras["n"] gives the repeat count.
    def _process_recognition(self, node, extras):
        sequence = extras["sequence"]   # A sequence of actions.
        
        for action in sequence:
            if (action != None):
                action.execute()

#---------------------------------------------------------------------------
# Create and load this module's grammar.


grammar.add_rule(SequenceRule())    # Add the top-level rule.

grammar.load()
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None

