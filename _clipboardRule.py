from dragonfly import *
import re

grammar = Grammar("clipboardGrammer")

class ClipWrap():
    initArray = [
        "empty zero",
        "empty one",
        "empty two",
        "empty three",
        "empty four",
        "empty five",
        "empty six",
        "empty seven",
        "empty eight",
        "empty nine"
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

def sayFromClipboard(n):
    print "test"
    print "-"+clip.clipboardArray[n]

    toMimic = ["say"]
    print toMimic
    text = formatStringToWords(clip.clipboardArray[n])
    print text
    toMimic.extend(text)
    print toMimic
    test = Mimic()
    test._words = tuple(toMimic)
    print test._words
    test.execute()

    print "End test"


def formatStringToWords(str):
    modifyStr = str.replace(",", r" ,\comma");
    modifyStr = str.replace(".", r" .\dot");
    modifyStr = str.replace("!", r" !\exclamation-mark");
    modifyStr = str.replace("?", r" !\question-mark");
    print modifyStr
    return re.sub(r'[^., \t\w]*', '', modifyStr).split()
    #return re.sub("[^\w]", " ",  modifyStr).split()



class extraClipboardMappingRule(MappingRule):
    mapping = {
        "copy [to [clipboard]] <n>" : Function(clipboardCopy),
        "past [from [clipboard]] <n>" : Function(clipboardPaste),
        "say from Clipboard <n>" : Function(sayFromClipboard)

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
