from Tkinter import Tk, Text, E, N,S, W, BOTH, StringVar, IntVar, Listbox, VERTICAL
from ttk import Frame, Button, Label, Style, Entry, Checkbutton, OptionMenu, Scrollbar


class CommunicationProtocal():
        
    def __init__(self):
        self.initGUI()

    def initGUI(self):
        self.tkRoot = Tk(baseName="")
        self.tkRoot.geometry("350x255+0+0")
        self.tkRoot.title("Mimic Commands Windows")

        frame = Frame(self.tkRoot)
        frame.style = Style()
        frame.style.theme_use("alt")
        frame.pack(fill=BOTH, expand=1)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(7, pad=7)
        frame.rowconfigure(12, weight=1)
        frame.rowconfigure(12, pad=7)
        
        labelLabelStart = Label(frame, text="Start:")
        labelLabelStart.grid(row = 0, column=0)
        self.labelStart = Label(frame, text="0")
        self.labelStart.grid(row = 1, column=0)

        labelLabelLength = Label(frame, text="Length:")
        labelLabelLength.grid(row = 0, column=1)
        self.labelLength = Label(frame, text="0")
        self.labelLength.grid(row = 1, column=1)

        labelLabelTotal = Label(frame, text="Total:")
        labelLabelTotal.grid(row = 0, column=2)
        self.labelTotal = Label(frame, text="0")
        self.labelTotal.grid(row = 1, column=2)
        

        self.labelStart = Label(frame, text="this is a")
        self.labelStart.grid(row = 2, column=0, sticky=E)
        self.labelStart = Label(frame, text="nice", foreground="red")
        self.labelStart.grid(row = 2, column=1)
        self.labelStart = Label(frame, text="test case I")
        self.labelStart.grid(row = 2, column=2, sticky=W, columnspan=2)   

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        self.labelQueueToSpeak = Label(frame, text="Queue to speak:")
        self.labelQueueToSpeak.grid(row = 3, column=0, pady=4, padx=5, sticky=W)

        self.listboxQueueToSpeak = Listbox(frame, width=50, height=3, yscrollcommand=scrollbar.set)
        self.listboxQueueToSpeak.insert(1, "1: Python")
        self.listboxQueueToSpeak.insert(2, "2: Perl")
        self.listboxQueueToSpeak.insert(3, "3: C")
        self.listboxQueueToSpeak.insert(4, "4: PHP")
        self.listboxQueueToSpeak.insert(5, "5: JSP")
        self.listboxQueueToSpeak.insert(6, "6: Ruby")
        
        scrollbar.config(command=self.listboxQueueToSpeak.yview)
        self.listboxQueueToSpeak.grid( sticky=N+S+E+W, row = 4, column = 0, columnspan = 2 ,rowspan = 3, padx=3)
        scrollbar.grid(sticky=N+S+W, row = 4, column = 2, rowspan = 3)

        self.buttonExecute = Button(frame, text="Pauze")
        self.buttonExecute.grid(row = 4, column=3)

        self.buttonExecute = Button(frame, text="Stop")
        self.buttonExecute.grid(row = 5, column=3)

        self.buttonExecute = Button(frame, text="Resume")
        self.buttonExecute.grid(row = 6, column=3)

        self.labelToSpeak = Label(frame, text="text to say:")
        self.labelToSpeak.grid(row = 7, column=0, padx=3, sticky=W)

        self.stringVarMimicCommand = StringVar()
        self.entryMimicCommand = Entry(frame, textvariable=self.stringVarMimicCommand, width=500)
        self.entryMimicCommand.grid(row=8, column=0, columnspan=3, padx=3, sticky=W)
        self.stringVarMimicCommand.set("hello SAPI Speak Engine")

        self.buttonExecute = Button(frame, text="say")
        self.buttonExecute.grid(row = 8, column=3)

        self.buttonExecute = Button(frame, text="prev voice")
        self.buttonExecute.grid(row = 10, column=0, padx=3, sticky=W)

        self.buttonExecute = Button(frame, text="next voice")
        self.buttonExecute.grid(row = 10, column=3)


        self.labelToSpeak = Label(frame, text="voice:")
        self.labelToSpeak.grid(row = 9, column=0, padx=3, sticky=W)

        var = StringVar(self.tkRoot)
        var.set("one") # initial value
        optionMenuQueueToSpeak = OptionMenu(frame, var, "one", "two", "three", "four")
        optionMenuQueueToSpeak.config(width=500)
        optionMenuQueueToSpeak.grid(sticky=W, row = 10, column = 1)
     
        self.tkRoot.protocol("WM_DELETE_WINDOW", self.HideOnClose)
        self.tkRoot.mainloop()  

        


    def HideOnClose(self):
        self.tkRoot.withdraw() # hide
        # root.quit()
        # root.deiconify()

if __name__ == '__main__':
    bla = CommunicationProtocal()