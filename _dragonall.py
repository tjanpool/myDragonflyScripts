from dragonfly import (Grammar, AppContext, MappingRule,
                       Key, Mimic, Integer, Function)

grammar = Grammar("dragon")

class dragonMappingRule(MappingRule):
    mapping = {
        "slap [<n>] [times]" : Key("enter:%(n)d"),
		"snore" : Key("npdiv"),
        "I am one with my computer" : Mimic( "say", "I", "am", "the", "terminator" ),
	}
    extras = [
            Integer("n", 1, 1000)
           ]
    defaults = {
                "n": 1,
               }

dragon_rule = dragonMappingRule()
grammar.add_rule(dragon_rule)
grammar.load()
# Unload function which will be called by natlink at unload time.
def unload():
	global grammar
	if grammar:
		grammar.unload()
		grammar = None
