import threading
from dragonfly import (Grammar, AppContext, MappingRule,
                       Key, Mimic, Integer, Function)
import sys
import os
import re 
import threading
import time

import natlink

from Tkinter import Tk, Text, BOTH, W, N, E, S, StringVar, IntVar
from ttk import Frame, Button, Label, Style, Entry, Checkbutton


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.counter = 0
        self.parent = parent
        self.parent.title("Windows")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(4, pad=7)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(4, pad=7)
        
        self.labelMimicCommand = Label(self, text="Command to Mimic:")
        self.labelMimicCommand.grid(sticky=W, pady=4, padx=5)

        self.stringVarMimicCommand = StringVar()
        self.entryMimicCommand = Entry(self, textvariable=self.stringVarMimicCommand, width=32)
        self.entryMimicCommand.grid(row=0,column=1, columnspan=3, rowspan=1, pady=4, padx=5)
        self.stringVarMimicCommand.set("say hello Dragonfly")

        self.buttonExecute = Button(self, text="Execute", command=self.CallbackButtonExecute)
        self.buttonExecute.grid(row = 1, column=0, columnspan=4)

        self.checkVarUseCounter = IntVar()
        self.checkboxUseCounter = Checkbutton(self, text = "Make use of the counter", variable = self.checkVarUseCounter, width=50)
        self.checkboxUseCounter.grid(sticky=W,row=2,column=0, columnspan=2, pady=2, padx=5)

        self.labelMimicCommand = Label(self, text="Seconds to countdown:")
        self.labelMimicCommand.grid(sticky=W, row = 3, column=0)

        self.intVarCounterInput = IntVar()
        self.intVarCounterInput.set(10)
        
        vcmd = (self.register(self.OnValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entryCounterInput = Entry(self, textvariable=self.intVarCounterInput, validate="key", validatecommand=vcmd, width=5)
        self.entryCounterInput.grid(sticky=W, row=3,column=1, pady=2, padx=5)

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
        toMimicTupleString = str(tuple(self.formatStringToWords(self.stringVarMimicCommand.get())))
        natlink.natConnect()
        natlink.setMicState( "off" )
        natlink.natDisconnect()
        filename = "..//_TestMimic"+str(self.counter)+".py"
        self.counter += 1
        self.CreateMimicFile(filename, toMimicTupleString)
        natlink.natConnect()
        natlink.setMicState( "on" )
        time.sleep(1)
        natlink.setMicState( "off" )
        natlink.natDisconnect()
        
        t = threading.Thread(target=self.deleteFile, args=(filename,))
        # t.daemon = True // thread dies to quick with this
        t.start()

    def deleteFile(self, filename):
        repeat = True
        while repeat:
            try:
                os.remove(filename)
                repeat = False
            except Exception, e:
                time.sleep(10)
        repeat = True
        while repeat:
            try:
                os.remove(filename+"c")
                repeat = False
            except Exception, e:
                time.sleep(10)
        

    def CreateMimicFile(self, filename,toMimicTupleString):
        target = open (filename, 'w') 

        target.write('from dragonfly import *\n')
        target.write('\n')
        target.write('mimic = Mimic'+toMimicTupleString+'\n')
        target.write('mimic.execute()\n')
        target.flush()
        target.close()
        # #create a mimic object
        # test = Mimic()
        # # Hacking the private/protected variable of the mimic object so it contains a tupple with what to mimic.
        # test._words = tuple(toMimic)
        # #execute mimic
        # test.execute()

    def formatStringToWords(self, str):
        modifyStr = str.replace(",", r" ,\comma")
        modifyStr = modifyStr.lower()
        modifyStr = modifyStr .replace(".", r" .\dot")
        modifyStr = modifyStr .replace("!", r" !\exclamation-mark")
        modifyStr = modifyStr .replace("?", r" !\question-mark")
        return re.sub(r'[^., \t\w]*', '', modifyStr).split()

    def Output(self, text):
        sys.stdout.write(text + '\n')
        sys.stdout.flush()

if __name__ == '__main__':
    root = Tk(baseName="")
    root.geometry("350x110+0+0")
    app = Example(root)
    root.mainloop()  
