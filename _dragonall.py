from dragonfly import (Grammar, AppContext, MappingRule, Dictation, IntegerRef,
                       Key, Text, Mimic)

grammar = Grammar("dragon")
dragon_rule = MappingRule(
		name = "dragon",
		mapping = {
            "slap" : Key("enter"),
			"snore" : Key("npdiv"),
                        "Transfer to emacs" : Key("c-a, c-c, a-f4/90, c-g, c-y"),
#                        "dictate": Mimic("show","dictation","box"),
		},
		extras = []
)

grammar.add_rule(dragon_rule)
grammar.load()
# Unload function which will be called by natlink at unload time.
def unload():
	global grammar
	if grammar:
		grammar.unload()
		grammar = None
