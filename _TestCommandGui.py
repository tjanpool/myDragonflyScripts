import threading
from dragonfly import (Grammar, AppContext, MappingRule,
                       Key, Mimic, Integer, Function)

import re 

from Tkinter import Tk, Text, BOTH, W, N, E, S, StringVar, IntVar
from ttk import Frame, Button, Label, Style, Entry, Checkbutton


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        print "init"
        self.parent = parent
        self.parent.title("Windows")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        print "pack"
        self.columnconfigure(1, weight=1)
        self.columnconfigure(4, pad=7)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(4, pad=7)
        
        print "labelMimicCommand"
        self.labelMimicCommand = Label(self, text="Command to Mimic:")
        self.labelMimicCommand.grid(sticky=W, pady=4, padx=5)
        print "entryMimicCommand"
        self.stringVarMimicCommand = StringVar()
        self.entryMimicCommand = Entry(self, textvariable=self.stringVarMimicCommand, width=32)
        self.entryMimicCommand.grid(row=0,column=1, columnspan=3, rowspan=1, pady=4, padx=5)
        self.stringVarMimicCommand.set("say hello Dragonfly")
        print "buttonExecute"
        self.buttonExecute = Button(self, text="Execute", command=self.CallbackButtonExecute)
        self.buttonExecute.grid(row = 1, column=0, columnspan=4)
        print "checkboxUseCounter"
        self.checkVarUseCounter = IntVar()
        self.checkboxUseCounter = Checkbutton(self, text = "Make use of the counter", variable = self.checkVarUseCounter, width=50)
        self.checkboxUseCounter.grid(sticky=W,row=2,column=0, columnspan=2, pady=2, padx=5)
        print "labelMimicCommand"
        self.labelMimicCommand = Label(self, text="Seconds to countdown:")
        self.labelMimicCommand.grid(sticky=W, row = 3, column=0)

        self.intVarCounterInput = IntVar()
        self.intVarCounterInput.set(10)
        
        vcmd = (self.register(self.OnValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entryCounterInput = Entry(self, textvariable=self.intVarCounterInput, validate="key", validatecommand=vcmd, width=5)
        self.entryCounterInput.grid(sticky=W, row=3,column=1, pady=2, padx=5)

        print "labelAnnounceCounter"
        self.labelAnnounceCounter = Label(self, text="Counter: 0")
        self.labelAnnounceCounter.grid(row = 3, column=2, columnspan=1)

    def OnValidate(self, d, i, P, s, S, v, V, W):
        # print "OnValidate:"
        # print "d='%s'" % d
        # print "i='%s'" % i
        # print "P='%s'" % P
        # print "s='%s'" % s
        # print "S='%s'" % S
        # print "v='%s'" % v
        # print "V='%s'" % V
        # print "W='%s'" % W
        try :
            int(S)
            return True
        except ValueError:
            return False

    def CallbackButtonExecute(self):
        if (self.checkVarUseCounter.get() == 1):
            counter = self.intVarCounterInput.get()
            self.Countdown(counter)
        else:
            self.Execute()


    def Countdown(self, remaining = None):
        if remaining is not None:
            self.remaining = remaining

        if self.remaining <= 0:
            self.labelAnnounceCounter.configure(text="Execute!")
            self.Execute()
        else:
            newCounterText = "Counter: "+str(self.remaining)
            self.labelAnnounceCounter.configure(text=newCounterText)
            self.remaining = self.remaining - 1
            self.after(1000, self.Countdown)
        
    def Execute(self):
        toMimic = ["say"]
        text = self.formatStringToWords(self.stringVarMimicCommand.get())
        toMimic.extend(text)

        #create a mimic object
        test = Mimic()
        # Hacking the private/protected variable of the mimic object so it contains a tupple with what to mimic.
        test._words = tuple(toMimic)
        #execute mimic
        test.execute()

    def formatStringToWords(self, str):
        modifyStr = str.replace(",", r" ,\comma");
        modifyStr = modifyStr .replace(".", r" .\dot");
        modifyStr = modifyStr .replace("!", r" !\exclamation-mark");
        modifyStr = modifyStr .replace("?", r" !\question-mark");

        # created a string: "Some ugly ,\comma but nice text to test .\dot"
        # now return an array by splitting on the spaces and I also believe removing non parsed things.
        # not sure about that piece.
        return re.sub(r'[^., \t\w]*', '', modifyStr).split()


def GuiThread():  
    print "gui Thread"
    root = Tk(baseName="")
    root.geometry("350x110+0+0")
    app = Example(root)
    print "Start mainloop"
    root.mainloop()  

grammar = Grammar("showTestCommandWindow")

def showTestCommandWindow():
    t = threading.Thread(target=GuiThread)
    # t.daemon = True
    t.start()

class TestCommandGuiMappingRule(MappingRule):
    mapping = {
        "show test command window": Function(showTestCommandWindow),
    }
    extras = [
            ]

testCommandGuiMappingRule = TestCommandGuiMappingRule()
grammar.add_rule(testCommandGuiMappingRule)
grammar.load()
print "grammar loaded"
# Unload function which will be called by natlink at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
        grammar = None
