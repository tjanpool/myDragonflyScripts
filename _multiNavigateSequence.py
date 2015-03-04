from dragonfly import *

class KeystrokeRule(MappingRule):
    exported = False

    mapping  = {
     # Spoken-form    ->    ->    ->     Action object
       "[<n>] up":                         Key("up:%(n)d"),
       "[<n>] down":                       Key("down:%(n)d"),
       "[<n>] left":                       Key("left:%(n)d"),
       "[<n>] right":                      Key("right:%(n)d"),
       "[<n>] words right":                Key("c-right:%(n)d"),
       "[<n>] words left":                Key("c-left:%(n)d"),
    }
    extras   = [
                IntegerRef("n", 1, 100),
                Dictation("text"),
                Dictation("text2"),
               ]
    defaults = {
                "n": 1,
               }
#---------------------------------------------------------------------------
# Here we create an element which is the sequence of keystrokes.

# First we create an element that references the keystroke rule.
#  Note: when processing a recognition, the *value* of this element
#  will be the value of the referenced rule: an action.
alternatives = []
alternatives.append(RuleRef(rule=KeystrokeRule()))
single_action = Alternative(alternatives)
sequence = Repetition(single_action, min=1, max=16, name="sequence")

class RepeatRule(CompoundRule):
    # Here we define this rule's spoken-form and special elements.
    spec     = "[<mainAction>]<sequence>"
    
    mainAction  = {
                "go":   0,
                "mark": 1,
               }
    extras   = [
                sequence,                 # Sequence of actions defined above.
                Choice("mainAction", mainAction),
               ]
    defaults = {
      "mainAction" : 0
    }

    # This method gets called when this rule is recognized.
    # Arguments:
    #  - node -- root node of the recognition parse tree.
    #  - extras -- dict of the "extras" special elements:
    #     . extras["sequence"] gives the sequence of actions.
    #     . extras["n"] gives the repeat count.
    def _process_recognition(self, node, extras):
        sequence = extras["sequence"]   # A sequence of actions.
        mainAction = extras["mainAction"]
        
        if mainAction == 1:
            Key("shift:down").execute()

        for action in sequence:
            action.execute()

        if mainAction == 1:
            Key("shift:up").execute()


#---------------------------------------------------------------------------
# Create and load this module's grammar.

grammar = Grammar("multiNavigation")   # Create this module's grammar.
grammar.add_rule(RepeatRule())    # Add the top-level rule.
grammar.load()                    # Load the grammar.

# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
