import sys
import pyttsx
import threading
import multiprocessing
import json
import time
import argparse
import re
from collections import deque 
import os
from Queue import Empty
from Tkinter import Tk, Text, E, N,S, W, BOTH, StringVar, IntVar, Listbox, VERTICAL
from ttk import Frame, Button, Label, Style, Entry, Checkbutton, OptionMenu, Scrollbar

settingsFileName = r'c:\natlink\natlink\macrosystem\Tools\sapispeakersettings.json'

class InputUserProcess():
    def run(self, inputQueue, filenoStdin):
        sys.stdin = os.fdopen(filenoStdin)  #open stdin in this process
        some_str = ""
        go = True;
        while go:
            some_str = raw_input("> ")

            if some_str.lower() == "quit":
                go = False;
            inputQueue.put_nowait(some_str)

class CommunicationProtocal():
    def __init__(self, useRawLine, cleanSettingsFileOnStartup):
        if os.path.isfile(settingsFileName) and cleanSettingsFileOnStartup:
            os.remove(settingsFileName)

        if useRawLine:
            inp = raw_input()

        self._inputQueue = multiprocessing.Queue()     
        self.recoveryTask = "recoverNextVoice"
        
        self.gui = EngineGui(self)
        self.initAPI()
        self.gui.StartGui()
        
    def initAPI(self):
        self.Output("initAPI")
        self._infoForProcQ = None
        self._infoForThisQ = None
        self._waitForText = False
        
        engineThread = threading.Thread(target=self.initEngineProcess)
        engineThread.start()
        
        self.GUIVisible = True
        self.CurrentVoiceName = ""
        self.CurrentRate = 0
        self._lastAction = None
        self._needRecovering = False
        self.OnWordStartLocation = None
        self.OnWordLength = 0
        self.OnWordTotal = 0
        self.SpeakQueue = deque()
        self.inputHandleThread = threading.Thread(target=self.InputLoop, args=(self.gui,))
        self.inputHandleThread.deamon = True
        self.inputHandleThread.start()


    def Output(self, text):
        sys.stdout.write(text + '\n')
        sys.stdout.flush()

    def InputLoop(self, gui):
        self.loop = True
        while (self.loop):
            try:
                inp = self._inputQueue.get(block=True)
       
                if (inp == "help"):
                    helpString = "key commands seperated by comma and only one accepted on each > are:\n stop -> to stop speaking,\n next voice -> switch voice next,\n previous voice -> switch voice to previous,\n speed up -> speed up by 10 rate of words sad per minut,\n speed down -> speed down by 10 as long rate >= 30, else keep current rate of words sad per minut,\n set speed [number] -> set the rate yourself without 30 as border, so possible risks are your own (verry low risk),\n say [text] -> say + the text you wish spoken,\n quit -> quits this application.\n"
                    print(helpString + "\n")
                elif (inp[:4] == "stop"):
                    self.restartProcess()
                elif (inp[:10] == "next voice"):
                    self.handleNextVoice()
                elif (inp[:len("previous voice")] == "previous voice"):
                    self.handlePrevVoice()
                elif (inp[:len("set voice")] == "set voice"):
                    self.handleSetVoice(inp[len("set voice "):])
                elif (inp[:8] == "speed up"):
                    self.handleSpeedUp()
                elif (inp[:10] == "speed down"):
                    self.handleSpeedDown()
                elif (inp[:10] == "set speed "):
                    inpSplitIntoSpaces = inp.split(' ')
                    self.handleSetSpeed(inpSplitIntoSpaces[2])
                elif (inp[:4] == "say "):
                    self.handleSay(inp[4:])
                elif (inp[:len("pauze")] == "pauze"):
                    self.handlePauze()
                elif (inp[:len("resume")] == "resume"):
                    self.handleResume()
                elif (inp[:len("show gui")] == "show gui"):
                    self.GUIVisible = True
                elif (inp[:len("hide gui")] == "hide gui"):
                    self.GUIVisible = False
                elif (inp[:4] == "quit"): # exit
                    self.loop = False
                    self.TerminateProcess()
                    print("-----exit func called")
                    gui.Close()
                else:
                    self.Output("err: not implementated or not recognized action: " + inp + ". didn't you forget to add something? please try again or type help for help or quit to terminate!")
            except Empty:
                time.sleep(0.1)
        print "end input thread"

    def handleSay(self, text):
        #self._say = True
        text = re.sub(r'[^., \t\w]*', '', text)
        if (text == ''):
            text = "recieved invalid text"
        self.SpeakQueue.append(text)
        self.Output("handledSay")
        #self._say = False
        if self.OnWordStartLocation == None and self._lastAction == None:
            self.OnWordStartLocation = 0
            self.OnWordLength = 0
            self.sendTextToSay()

    def handlePauze(self):
        self.restartEngine()
        textToSay = self.obtainTextToSend()
        self.SpeakQueue[0] = textToSay 

    def handleResume(self):
        self.restartEngine()
        self.sendTextToSay();

    def handleNextVoice(self):
        self.recoveryTask = "recoverNextVoice"
        self.handleNextVoiceBaseLikeActions("handleNextVoice", "doNextVoice")

    def handlePrevVoice(self):
        self.recoveryTask = "recoverPrevVoice"
        self.handleNextVoiceBaseLikeActions("handlePrevVoice", "doPrevVoice")

    def handleSetVoice(self, voiceToSelect):
        self.Output("set voice action")
        if (len(voiceToSelect) == 0):
            self.Output("You should give something that at least looks like a voice")
        else:
            if (self._lastAction != None and not self._needRecovering):
                self.restartEngine()
            
            self.recoveryTask = "recoverSetVoice"
            if (self.wordTotal == 0):
                self._lastAction = "introduce"

            if (self.SpeakQueue):
                textToSay = self.obtainTextToSend()
                self.SpeakQueue[0] = textToSay 
            self._infoForProcQ.put("setVoice " + voiceToSelect)


    def handleSpeedUp(self):
        self.handleNextVoiceBaseLikeActions("handleSpeedUp", "doSpeedUp")

    def handleSpeedDown(self):
        self.handleNextVoiceBaseLikeActions("handleSpeedDown", "doSpeedDown")

    def handleSetSpeed(self, rate):
        self.handleNextVoiceBaseLikeActions("handleSetSpeed note:number below 30 means keep current speed", "doSetSpeed " + str(rate))

    def obtainTextToSend(self):
        return self.SpeakQueue[0][self.OnWordStartLocation: len(self.SpeakQueue[0])]
        
    def sendTextToSay(self):
        self._lastAction = "saySomething"
        self._infoForProcQ.put("textToSay " + self.obtainTextToSend())
        self.Output("giveText")

    def handleNextVoiceBaseLikeActions(self, feedbackCommand, firstInCommand):
        if (self._lastAction != None and not self._needRecovering):
            self.restartEngine()

        self.Output(feedbackCommand)
        if self.SpeakQueue:
            self._lastAction = "saySomething"
            textToSay = self.obtainTextToSend()
            # change the text in queue, The counter resets, and we don't want
            # to end up at new spot after nextVoice
            self.SpeakQueue[0] = textToSay 
            self._infoForProcQ.put(firstInCommand + " textToSay " + textToSay)
        else:
            self._lastAction = "introduce"
            self._infoForProcQ.put(firstInCommand + " introductionCommand")

    def restartEngine(self):
        self.TerminateProcess()
        self.initEngineProcess()

    def restartProcess(self):
        self.loop = False
        self.TerminateProcess()
        self.initAPI()

    def initEngineProcess(self):
        self.Output("initEngine")
        speakEngineProcess = SpeakEngineProcess() # class is just a distancation.  normally would just use a diff, so class is
                                                  # useless
        
        self._infoForProcQ = multiprocessing.Queue()
        self._infoForThisQ = multiprocessing.Queue()
        self._actualProcess = multiprocessing.Process(target=speakEngineProcess.Run, args=(self._infoForThisQ, self._infoForProcQ,))
        self._actualProcess.deamon = True
        self._actualProcess.start()
     
        self.lisenThread = threading.Thread(target=self.listernerToSpeakProcess, args=(self._infoForThisQ,))
        self.lisenThread.daemon = True
        self.lisenThread.start()        

    def listernerToSpeakProcess(self, infoForthisQ):
        keepLisening = True
        while (keepLisening):
            try:
                input = infoForthisQ.get(block=True)
                self._finished = False # possible deadlock senario in model.  This is one part of prefenting it.
                self.Output(input)

                if ('loadedSettings' in input):
                    fn = sys.stdin.fileno() 
                    inputSplitIntoSpaces = input.split(' ')
                    self.CurrentRate = int(inputSplitIntoSpaces[2])
                    self.CurrentVoiceName = "";
                    for x in range (4, len(inputSplitIntoSpaces)-1):
                        self.CurrentVoiceName += inputSplitIntoSpaces[x]+" "
                    self.CurrentVoiceName += inputSplitIntoSpaces[len(inputSplitIntoSpaces)-1] 

                    inputReader = InputUserProcess()
                    self._inputProcess = multiprocessing.Process(target=inputReader.run, args=(self._inputQueue,fn))
                    self._inputProcess.Deamon = True
                    self._inputProcess.start()
                elif ('starting' in input):
                    self.OnWordStartLocation = 0
                    if not self._lastAction == "introduce":
                        self.OnWordTotal = len(self.SpeakQueue[0])
                    else:
                        self.OnWordStartLocation = 0
                        self.OnWordTotal = 0
                elif ('onWord' in input):
                    # if not self._lastAction == "introduce":
                    inputSplitIntoSpaces = input.split(' ')
                    # [0]:onWord [1]:<id> [2]:location: [3]:<int>
                    # [4]:length ...  [10]: voiceName(hack)
                    self.OnWordStartLocation = int(inputSplitIntoSpaces[3])
                    self.OnWordLength =  int(inputSplitIntoSpaces[5])

                    # hack for setting voice recovery.
                    self.CurrentVoiceName = "";
                    for x in range (10, len(inputSplitIntoSpaces)-1):
                        self.CurrentVoiceName += inputSplitIntoSpaces[x]+" "
                    self.CurrentVoiceName += inputSplitIntoSpaces[len(inputSplitIntoSpaces)-1] 
                      
                elif ('onError' in input):
                    self._needRecovering = True
                    self.restartEngine()
                    if self.recoveryTask == "recoverNextVoice":
                        self.handleNextVoice()  #<----------------------- error because lastaction.
                    elif self.recoveryTask == "recoverPrevVoice":
                        self.handlePrevVoice()  #<----------------------- error because lastaction.
                    elif self.recoveryTask == "recoverSetVoice":
                    	self.SpeakQueue.appendright("The voice you wished to select seemed to be invalid")          
                    	self.handleSetVoice(self.CurrentVoiceName)
                    	# rather be stupid, then stuck.  so a kind of fail save,
                    	# setting other recovery task.
                    	self.recoveryTask = "recoverNextVoice"
                    self._needRecovering = False
                elif('finished' in input):
                    self.OnWordLength = 0
                    if not self._lastAction == "introduce":
                        self.SpeakQueue.popleft()

                    if self.SpeakQueue:         # if SpeakQueue has items
                        self.OnWordStartLocation = 0
                        self.OnWordTotal = len(self.SpeakQueue[0])
                        self.sendTextToSay()
                    else:
                        self.OnWordStartLocation = None
                        self.OnWordTotal = 0
                        self.Output("EndSpeakSignal")
                        self._infoForProcQ.put("EndSpeakSignal")
                elif('loopEnded' in input):
                    self._inputProcess.terminate()

                    self._lastAction = None
                    self.initEngineProcess()
                    # new process created, so stop looping in this loop.
                    keepLisening = False
                elif(input[:len('doSpeed')] == 'doSpeed'):
                    inputSplitIntoSpaces = input.split(' ')
                    self.CurrentRate = int(inputSplitIntoSpaces[2])
            except Empty:
                time.sleep(0.1)
            
            
    def TerminateProcess(self):
        if self._actualProcess != None:
            if self._actualProcess.is_alive():
                self._inputProcess.terminate()
                self._actualProcess.terminate()
                self.Output("terminateProcess")           
                self._infoForProcQ = None
                self._infoForThisQ = None

class EngineGui():
    def __init__(self, communicationProtocal):
        self.communicationProtocal = communicationProtocal

    def StartGui(self):
        self.tkRoot = Tk(baseName="")
        self.tkRoot.geometry("350x300+0+0")
        self.tkRoot.title("Engine SAPI GUI")
        self.GUIVisible = True

        frame = Frame(self.tkRoot)
        frame.style = Style()
        frame.style.theme_use("alt")
        frame.pack(fill=BOTH, expand=1)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(7, pad=7)
        frame.rowconfigure(13, weight=1)
        frame.rowconfigure(13, pad=7)
        
        Label(frame, text="Start:").grid(row = 0, column=0)
        self.labelStart = Label(frame, text="0")
        self.labelStart.grid(row = 1, column=0)

        Label(frame, text="Length:").grid(row = 0, column=1)
        self.labelLength = Label(frame, text="0")
        self.labelLength.grid(row = 1, column=1)

        Label(frame, text="Total:").grid(row = 0, column=2)
        self.labelTotal = Label(frame, text="0")
        self.labelTotal.grid(row = 1, column=2)
        
        self.labelSentenceLeft = Label(frame, text="...")
        self.labelSentenceLeft.grid(row = 2, column=0, sticky=E)
        self.labelSentenceSpoken = Label(frame, text="...", foreground="red")
        self.labelSentenceSpoken.grid(row = 2, column=1)
        self.labelSentenceRight = Label(frame, text="...")
        self.labelSentenceRight.grid(row = 2, column=2, sticky=W, columnspan=2)   

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        self.labelQueueToSpeak = Label(frame, text="Queue to speak:").grid(row = 3, column=0, pady=4, padx=5, sticky=W)
        self.listboxQueueToSpeak = Listbox(frame, width=50, height=3, yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.listboxQueueToSpeak.yview)
        self.listboxQueueToSpeak.grid( sticky=N+S+E+W, row = 4, column = 0, columnspan = 2 ,rowspan = 3, padx=3)
        scrollbar.grid(sticky=N+S+W, row = 4, column = 2, rowspan = 3)

        self.buttonPauze = Button(frame, text="Pauze", command=self.communicationProtocal.handlePauze)
        self.buttonPauze.grid(row = 4, column=3)

        self.buttonStop = Button(frame, text="Stop", command=self.communicationProtocal.restartProcess)
        self.buttonStop.grid(row = 5, column=3)

        self.buttonResume = Button(frame, text="Resume", command=self.communicationProtocal.handleResume)
        self.buttonResume.grid(row = 6, column=3)

        Label(frame, text="Text to say:").grid(row = 7, column=0, padx=3, sticky=W)

        self.stringVarTextToSay = StringVar()
        self.entryTextToSay = Entry(frame, textvariable=self.stringVarTextToSay, width=500)
        self.entryTextToSay.grid(row=8, column=0, columnspan=3, padx=3, sticky=W)
        self.stringVarTextToSay.set("Hello SAPI Speak Engine")
        self.entryTextToSay.bind('<Return>', self.CallBackReturnSay)

        self.buttonSay = Button(frame, text="Say", command=self.CallBackButtonSay)
        self.buttonSay.grid(row = 8, column=3)

        Label(frame, text="Recover action:").grid(row = 9, column=0, padx=3, sticky=W)
        self.recoverActionLabelText = "None"
        self.labelRecoverAction = Label(frame, text=self.recoverActionLabelText, foreground="blue")
        self.labelRecoverAction.grid(row = 10, column=0)   

        Label(frame, text="Voice speed:").grid(row = 9, column=1, sticky=W)
        self.buttonSpeedDown = Button(frame, text="Speed down", command=self.communicationProtocal.handleSpeedDown)
        self.buttonSpeedDown.grid(row = 10, column=1, padx=3, sticky=E)

        self.speedValue = 0
        self.intVarSpeed = IntVar()
        vcmd = (self.tkRoot.register(self.OnValidateEntrySpeakSpeed), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entrySpeakSpeed = Entry(frame, textvariable=self.intVarSpeed, validate="key", validatecommand=vcmd, width=5)
        self.entrySpeakSpeed.grid(row=10,column=2)
        self.entrySpeakSpeed.bind('<Return>', self.CallBackSetSpeed)

        self.buttonSpeedUp = Button(frame, text="Speed up", command=self.communicationProtocal.handleSpeedUp)
        self.buttonSpeedUp.grid(row = 10, column=3)

        Label(frame, text="voice:").grid(row = 11, column=0, padx=3, sticky=W)
        self.buttonPrevVoice = Button(frame, text="Prev voice", command=self.communicationProtocal.handlePrevVoice)
        self.buttonPrevVoice.grid(row = 12, column=0, padx=3, sticky=W)

        self.buttonNextVoice = Button(frame, text="Next voice", command=self.communicationProtocal.handleNextVoice)
        self.buttonNextVoice.grid(row = 12, column=3)

        self.currentVoice = StringVar(self.tkRoot)
        self.currentVoice.set(self.communicationProtocal.CurrentVoiceName)

        engine = pyttsx.init()
        voices = engine.getProperty("voices")
        voiceNames = list()
        for x in xrange(0, len(voices)):
            voiceNames.append(voices[x].name)
        self.optionMenuVoices = OptionMenu(frame, self.currentVoice, *tuple(voiceNames), command=self.CallBackOptionMenuVoices)
        self.optionMenuVoices.config(width=500)
        self.optionMenuVoices.grid(sticky=W, row = 12, column = 1)
     
        #hide if close button is clicked
        self.tkRoot.protocol("WM_DELETE_WINDOW", self.HideGui)
        self.tkRoot.after(1000/32, self.Update)
        self.tkRoot.mainloop()  

    def Update(self):
        wordLocation = self.communicationProtocal.OnWordStartLocation
        wordLength = self.communicationProtocal.OnWordLength
        wordTotal = self.communicationProtocal.OnWordTotal

        if wordLocation:
            self.labelStart.configure(text=wordLocation)
        else:
            self.labelStart.configure(text="0")
        self.labelLength.configure(text=wordLength)
        if wordLength != 0 and wordTotal == 0:
            self.labelTotal.configure(text="Introduce")    
        else:
            self.labelTotal.configure(text=wordTotal)

        if len(self.communicationProtocal.SpeakQueue) != 0:
            if (wordLocation < 25):
                self.labelSentenceLeft.configure(text=str(self.communicationProtocal.SpeakQueue[0])[0:wordLocation])
            else:
                self.labelSentenceLeft.configure(text=str(self.communicationProtocal.SpeakQueue[0])[wordLocation-25:wordLocation])
            self.labelSentenceSpoken.configure(text=str(self.communicationProtocal.SpeakQueue[0])[wordLocation:wordLocation+wordLength])
            if (wordTotal - wordLocation - wordLength < 25):
                self.labelSentenceRight.configure(text=str(self.communicationProtocal.SpeakQueue[0])[wordLocation+wordLength:wordTotal])
            else:
                self.labelSentenceRight.configure(text=str(self.communicationProtocal.SpeakQueue[0])[wordLocation+wordLength:wordLocation+wordLength+25])
        else:
            self.labelSentenceLeft.configure(text="...")
            self.labelSentenceSpoken.configure(text="...")
            self.labelSentenceRight.configure(text="...")

        if (self.communicationProtocal.SpeakQueue != None and self.listboxQueueToSpeak.size() != len(self.communicationProtocal.SpeakQueue)):
            self.listboxQueueToSpeak.delete(0,self.listboxQueueToSpeak.size())
            for x in xrange(0,len(self.communicationProtocal.SpeakQueue)):
                self.listboxQueueToSpeak.insert(x, str(x)+": "+self.communicationProtocal.SpeakQueue[x])

        if (self.currentVoice.get() != self.communicationProtocal.CurrentVoiceName):
            self.currentVoice.set(self.communicationProtocal.CurrentVoiceName)

        if self.speedValue != self.communicationProtocal.CurrentRate:
            self.intVarSpeed.set(self.communicationProtocal.CurrentRate) 
            self.speedValue = self.communicationProtocal.CurrentRate

        if self.recoverActionLabelText != self.communicationProtocal.recoveryTask:
            self.recoverActionLabelText = self.communicationProtocal.recoveryTask
            self.labelRecoverAction.configure(text=self.recoverActionLabelText)

        if self.GUIVisible != self.communicationProtocal.GUIVisible:
            # self.GUIVisible ? self.HideGui : self.ShowGui
            self.HideGui() if self.GUIVisible else self.ShowGui()
            
        self.tkRoot.after(1000/32,self.Update)

    def OnValidateEntrySpeakSpeed(self, d, i, P, s, S, v, V, W):
        try :
            int(S)
            return True
        except ValueError:
            return False

    def CallBackSetSpeed(self):
        self.communicationProtocal.handleSetSpeed(self.intVarSpeed.get())

    def CallBackReturnSay(self, event):
        self.CallBackButtonSay()

    def CallBackButtonSay(self):
        self.communicationProtocal.handleSay(self.stringVarTextToSay.get())
        
    def CallBackOptionMenuVoices(self, selectedItem):
        self.communicationProtocal.handleSetVoice(selectedItem)

    def Close(self):
        self.tkRoot.quit()
        
    def HideGui(self):
        self.GUIVisible = False
        self.communicationProtocal.GUIVisible = False
        self.tkRoot.withdraw()
        
    def ShowGui(self):
        self.GUIVisible = True
        self.communicationProtocal.GUIVisible = True
        self.tkRoot.deiconify()

class SpeakEngineProcess():
    def Run(self, infoForMainAppQ, infoForProcessQ):
        
        self._speakId = 0
        self._infoForMainAppQ = infoForMainAppQ
        self._infoForProcessQ = infoForProcessQ

        self.engine = pyttsx.init()

        self.engine.connect('started-utterance', self.onStart)
        self.engine.connect('started-word', self.onWord)
        self.engine.connect('finished-utterance', self.onEnd)
            
        self.engine.connect('error', self.onError)
        
        self._voices = self.engine.getProperty("voices")
        self._loadSettings()
        self.handleInput()

        self._infoForMainAppQ.put("startLoop")
        self.engine.startLoop()
        self._infoForMainAppQ.put("loopEnded")
        
    def handleInput(self):
        loop = True
        while loop:
            try:
                input = self._infoForProcessQ.get(block=True)
                loop = False
                self._infoForMainAppQ.put("test " + input)
                if input[:len("doNextVoice ")] == "doNextVoice ":
                    input = input[len("doNextVoice "):]
                    self._nextVoice()
                elif input[:len("doPrevVoice ")] == "doPrevVoice ":
                    input = input[len("doPrevVoice "):]
                    self._prevVoice()
                elif input[:len("doSpeedUp ")] == "doSpeedUp ":
                    input = input[len("doSpeedUp "):]
                    self._speedUp()
                elif input[:len("doSpeedDown ")] == "doSpeedDown ":
                    input = input[len("doSpeedDown "):]
                    self._speedDown()
                elif input[:len("doSetSpeed ")] == "doSetSpeed ":
                    inputSplitIntoSpaces = input.split(' ')
                    try:
                        newSpeed = int(inputSplitIntoSpaces[1])
                        self._setSpeed(newSpeed)
                        # input = cut off first part (doSetSpeed, <space>,
                        # newSpeed, <space>) so from [len[0]+len[1]+2 : till
                        # end ]
                        input = input[len(inputSplitIntoSpaces[0]) + len(inputSplitIntoSpaces[1]) + 2:]
                    except:
                        self._infoForMainAppQ.put("exspected " + inputSplitIntoSpaces[1] + " to be a number")
                elif input[:len("setVoice")] == "setVoice":
                    voice = input[len("setVoice "):]
                    self._infoForMainAppQ.put("set voice reached "+voice)
                    rValue = self._setVoice(voice)
                    if (rValue):
                        input = "textToSay voice is set "+voice
                    else:
                        input = "textToSay no such voice "+voice
                
                if input[:len("introductionCommand")] == "introductionCommand":
                    self._infoForMainAppQ.put("introduction command")
                    self._introduceVoice()
                elif input[:len("textToSay ")] == "textToSay ":
                    text = input[len("textToSay "):]
                    if (text != ''):       
                        self._speakId += 1
                        self.engine.say(text, self._speakId)
                elif ('EndSpeakSignal' in input):
                    self.engine.endLoop()
                
                else:
                    self._infoForMainAppQ.put("Miscommunication message is: " + str(input)) + " use stop command if you get stuck"
            except Empty:
                time.sleep(0.1)
    
    def _introduceVoice(self):
        text = "Hello, I am " + self._voiceName
        if ('NL' in self._voiceName):
            text = "Hallo, ik ben " + self._voiceName

        self._speakId += 1
        self.engine.say(text, self._speakId)

    def onStart(self, name):
        try:
            self._infoForMainAppQ.put(str('starting ' + str(name)))
        except: # wait, why didn't .put infoke a print???  maybe str and int problem, but this
                # is how you find it.
            print sys.exc_info()

    def onEnd(self, name, completed):
        self._infoForMainAppQ.put('finished ' + str(name) + ' ' + str(completed))
        self.handleInput()

    def onWord(self, name, location, length):
        self._infoForMainAppQ.put("onWord " + str(name) + " location: " + str(location) + " length: " + str(length) + " makes total: " + str(location + length) +" voice: "+self._voiceName)

    def onError(self, name, exception):
        self._infoForMainAppQ.put("onError " + str(name) + " " + str(exception))
    
    def _nextVoice(self):
        self._selectedVoiceIndex = self._selectedVoiceIndex + 1
        if (self._selectedVoiceIndex >= len(self._voices)):
            self._selectedVoiceIndex = 0
        self._infoForMainAppQ.put("doNextVoice voice=" + str(self._voices[self._selectedVoiceIndex].name))
        self.engine.setProperty('voice', self._voices[self._selectedVoiceIndex].id)
        self._saveSettings()

    def _setVoice(self, voiceToSelect):
        for x in xrange(0, len(self._voices)):
            self._infoForMainAppQ.put("is "+voiceToSelect+" in "+self._voices[x].name)
            if voiceToSelect in self._voices[x].name:
                self._selectedVoiceIndex = x
                self._infoForMainAppQ.put("doSetVoice voice")
                self.engine.setProperty('voice', self._voices[self._selectedVoiceIndex].id)
                self._saveSettings()
                return True
        self._infoForMainAppQ.put("noSuchVoice")
        return False

    def _prevVoice(self):
        self._selectedVoiceIndex = self._selectedVoiceIndex - 1
        if (self._selectedVoiceIndex < 0):
            self._selectedVoiceIndex = len(self._voices) - 1
        self._infoForMainAppQ.put("doPrevVoice voice=" + str(self._voices[self._selectedVoiceIndex].name))
        self.engine.setProperty('voice', self._voices[self._selectedVoiceIndex].id)
        self._saveSettings()

    def _setSpeed(self, newSpeed):
        self._currentRate = newSpeed
        self._infoForMainAppQ.put("doSetSpeed rate: " + str(self._currentRate))
        self.engine.setProperty('rate', self._currentRate)
        self._saveSettings()

    def _speedUp(self):
        self._currentRate = self._currentRate + 10
        self._infoForMainAppQ.put("doSpeedUp rate: " + str(self._currentRate))
        self.engine.setProperty('rate', self._currentRate)
        self._saveSettings()

    def _speedDown(self):
        if self._currentRate > 30:
            self._currentRate = self._currentRate - 10
        self._infoForMainAppQ.put("doSpeedDown rate: " + str(self._currentRate))
        self.engine.setProperty('rate', self._currentRate)
        self._saveSettings()

        
    def _loadSettings(self):
        data = None
        self._selectedVoiceIndex = 0
        self._currentRate = 180
        try:
            with open(settingsFileName) as file:
                data = json.load(file) 
        except IOError:
            self._saveSettings(False)
            try:
                with open(settingsFileName) as file:
                    data = json.load(file) 
            except IOError:
                self._infoForMainAppQ.put("got a real problem with creating and building settings.")

        if (data != None):
            self._selectedVoiceIndex = data[0]['voice']
            self._currentRate = data[0]['rate']
            self.engine.setProperty('rate', self._currentRate)
            self.engine.setProperty('voice', self._voices[self._selectedVoiceIndex].id)
        else:
            self._infoForMainAppQ.put("Something went terribly wrong!!!, could be a setting problem?")
        self._voiceName = self._voices[self._selectedVoiceIndex].name
        self._infoForMainAppQ.put("loadedSettings rate: "+str(self._currentRate)+" voice: "+self._voiceName)

    def _saveSettings(self, existed=True):
        data = [{ 'voice':self._selectedVoiceIndex, 'rate':self._currentRate }]
        with open(settingsFileName, 'w') as file:
            file.write(json.dumps(data, sort_keys=True, indent=4))
        if existed:
            self._infoForMainAppQ.put("savedSettings")
        else:
            self._infoForMainAppQ.put("generatedSettings")
        self._voiceName = self._voices[self._selectedVoiceIndex].name

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--useRawLine", help="use a raw_input read that has to be ensered before run. Used for testing with JTorx.", action="store_true", default=False)
    parser.add_argument("--cleanSettingsFileOnStartup", help="deletes the settings file on startup or not, Deleting it makes sure to get a clean start, then there will be generated a new one", action="store_true", default=False)
    args = parser.parse_args()
    CommunicationProtocal(args.useRawLine, args.cleanSettingsFileOnStartup)