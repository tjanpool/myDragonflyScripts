from dragonfly import *
import subprocess
import threading

UseGuiAtStart = True
class SubprocessController():
    def __init__(self):
        t = threading.Thread(target=self.createSubprocess)
        # t.daemon = True // thread dies to quick with this
        t.start()

    def listenToSubprocess(self, pipe):
        print "listening"
        for line in iter(pipe.readline, b''):
            print line
        pipe.close()
        
    def createSubprocess(self):
        print "engine started"
        self.testGuiProcess = subprocess.Popen(
                ['python',
                 'TestByMimicGui.py',
                 ],
                shell=True,
                cwd=r'C:\\NatLink\\NatLink\\MacroSystem\\Tools',
                stdout=subprocess.PIPE, # a pipe didn't receive a thing. this is blocked.
                )
        outThread = threading.Thread(target=self.listenToSubprocess, args=(self.testGuiProcess.stdout,))
        # outThread.daemon = True
        outThread.start()

    def KillProcess(self):
        # kill python process
        try:
            self.testGuiProcess.stdout.close()
            self.testGuiProcess.kill()
        except:
            pass # just because i like it.

def startGui():
    global GuiProcess
    if (GuiProcess != None):
        GuiProcess.KillProcess()
    GuiProcess = SubprocessController()

GuiProcess = None
if UseGuiAtStart:
    startGui()

class TestGUIMappingRule(MappingRule):
        mapping = {
            "StartTestGui" : Function(startGui), # text cast as variable text in function. Was hard to figure out.
        }
    
grammar = Grammar("TestGUIGrammer")
testGUIMappingRule = TestGUIMappingRule()
grammar.add_rule(testGUIMappingRule)
grammar.load()

def unload():
    global grammar
    if grammar:
        print "unload grammer of TestGui"
        global GuiProcess
        if (GuiProcess != None):
            GuiProcess.KillProcess()
        grammar.unload()
        grammar = None