from dragonfly import (Grammar, AppContext, MappingRule,
                       Key, Mimic, Integer, Function)
import time

grammar = Grammar("dragon")


# At the moment to sleep time is two seconds, if this is not enough, then there is a big chance the content of your
# file gets deleted if you say dictate. If this is the case then please raise the number in time.sleep(...).
# When Dragon calls its dictation box, then it fires first ctrl C but will copy the entire line in sublime text.
# Because I want to start without selected text. I select all text and deleted.
def dictate():
    Mimic("show","dictation","box").execute()
    time.sleep(2)
    Key("c-a, delete").execute()

class dragonMappingRule(MappingRule):
    mapping = {
        "slap [<n>] [times]" : Key("enter:%(n)d"),
		    "snore" : Key("npdiv"),
        "I am one with my computer" : Mimic( "say", "I", "am", "the", "terminator" ),
        "dictate": Function(dictate),
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
