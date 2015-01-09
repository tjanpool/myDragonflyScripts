from dragonfly import *
import re

grammar = Grammar("clipboardGrammer")

class ClipWrap():
    initArray = [
        u"empty zero",
        u"empty one",
        u"empty two",
        u"empty three",
        u"empty four",
        u"empty five",
        u"empty six",
        u"empty seven",
        u"empty eight",
        u"empty nine"
        ]

    clipboardArray = initArray

clip = ClipWrap()
def clipboardCopy(n):
    print "coppy to "+str(n)
    clipBoardInstance = Clipboard(from_system=True)
    temporary = Clipboard({Clipboard.format_unicode:clip.initArray[n]})
    temporary.copy_to_system()

    # copy new text to this set clipboard. If no text selected the text "didn't found selected text." remains on clipboard
    Key("c-c/25").execute()
    text = Clipboard(from_system=True).get_text()
    clip.clipboardArray[n] = text
    print clip.clipboardArray[n]
    # set the first original obtained clipboard back to the system.
    clipBoardInstance.copy_to_system()



def clipboardPaste(n):
    print "paste from "+str(n)
    clipBoardInstance = Clipboard(from_system=True)
    # Create temporary clipboard With text we want
    temporary = Clipboard({Clipboard.format_unicode:clip.initArray[n]})
    temporary.copy_to_system()

    # Paste the text
    Key("c-v/25").execute()

    # Restored the old clipboard
    clipBoardInstance.copy_to_system()

class extraClipboardMappingRule(MappingRule):
    mapping = {
        "copy [to [clipboard]] <n>" : Function(clipboardCopy),
        "past [from [clipboard]] <n>" : Function(clipboardPaste),
    }
    extras = [
            Integer("n", 0, 9)
    ]


clipping_rule = extraClipboardMappingRule()
grammar.add_rule(clipping_rule)
grammar.load()

# Unload function which will be called by natlink at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
        grammar = None
