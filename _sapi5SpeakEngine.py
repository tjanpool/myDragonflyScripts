from dragonfly import *
import subprocess
import threading
import Queue
import time
from dragonfly.windows.clipboard import Clipboard
import re

#don't forget to terminate <ctrl><shift><esc> the python processes if you can't save because acces denied. Probably 3 on the loose

# setup stuf to comminicate with engine process.
class SubprocessController():
	def __init__(self):
		self.sapiProcess = None
		t = threading.Thread(target=self.createSubprocess)
		t.daemon = True
		t.start()

	def listenToSubprocess(self, pipe):
		for line in iter(pipe.readline, b''):
			print line
		pipe.close()
		print "closed a pipe"

	def createSubprocess(self):
		print "engine started"
		self.sapiProcess = subprocess.Popen(
				['python',
				 'Engine.py',
				 ],
				shell=True,

				cwd=r'C:\\NatLink\\NatLink\\MacroSystem',
				stdout=subprocess.PIPE, # a pipe didn't receive a thing. this is blocked.
				stderr=subprocess.PIPE, # a pipe didn't receive a thing. this is blocked.
				#stderr=subprocess.PIPE, # thats way we are going to use a named pipe to communicate
				stdin=subprocess.PIPE,
				)
		outThread = threading.Thread(target=self.listenToSubprocess, args=(self.sapiProcess.stdout,))
		errThread = threading.Thread(target=self.listenToSubprocess, args=(self.sapiProcess.stderr,))

		outThread.daemon = True
		errThread.daemon = True

		outThread.start()
		errThread.start()
		print "output threads started"

	def CommandToEngine(self, input):
		print "input to give to proc = "+input
		#t = re.sub(r'[^a-zA-Z0-9 ]',r'',input)
		t = input.replace("\n", "")
		self.sapiProcess.stdin.write((t+"\n"))
		self.sapiProcess.stdin.flush()
		print "I wrote something"

def nextVoice():
	sapiControllor.CommandToEngine("next voice")

def prevVoice():
	sapiControllor.CommandToEngine("previous voice")

def setVoice(text):
	sapiControllor.CommandToEngine("set voice "+text)

def speedUp():
	sapiControllor.CommandToEngine("speed up")

def speedDown():
	sapiControllor.CommandToEngine("speed down")

def setSpeed(n):
	sapiControllor.CommandToEngine("set speed "+str(n))

def pauze():
	sapiControllor.CommandToEngine("pauze")

def resume():
	sapiControllor.CommandToEngine("resume")

def stop():
	sapiControllor.CommandToEngine("stop")

def sayOutLoud(text):
	sapiControllor.CommandToEngine("say "+str(text))

def redirectCommand(command):
	sapiControllor.CommandToEngine(command)

def readSelected():
	clipBoardInstance = Clipboard(from_system=True)
	# make a temporary clipboard, with the message didn't found selected text, and clone it to system.
	temporary = Clipboard({Clipboard.format_unicode: u"didn't found selected text."})
	temporary.copy_to_system()

	# copy new text to this set clipboard. If no text selected the text "didn't found selected text." remains on clipboard
 	Key("c-c/25").execute()
 	text = Clipboard(from_system=True).get_text()
	sayOutLoud(text.encode('utf8'))

	# set the first obtained clipboard back to the system.
	clipBoardInstance.copy_to_system()


#----------------Start rule preperation stuff -------------
grammar = Grammar("sapi5pyttsx")
sapiControllor = SubprocessController()

def killProcess():
		# kill python process36
		try:
			self.sapiProcess.stderr.close()
			self.sapiProcess.stdout.close()
			self.sapiProcess.stdin.close()
			self.sapiProcess.kill()
		except:
			pass # just because i like it.

class SapiMappingRule(MappingRule):
        mapping = {
			"[computer] say <text>" : Function(sayOutLoud), # text cast as variable text in function. Was hard to figure out.
			"read selected [text]" : Function(readSelected),
			"next voice" : Function(nextVoice),
			"previous voice" : Function(prevVoice),
			"set voice " : Function(setVoice),
			"set speed " : Function(setSpeed),
			"speed up" : Function(speedUp),
			"speed down" : Function(speedDown),
			"pauze" : Function(pauze),
			"resume" : Function(resume),
			"stop" : Function(stop),
		}
	extras = [	Integer("n", 10, 500),
			Dictation("text")
                ]
	defaults = {
				"n": 300,
			   }
sapiRule = SapiMappingRule()
grammar.add_rule(sapiRule)
grammar.load()

def unload():
	global grammar
	if grammar:
		print "unload grammer of _sapi5SpeakEngine"
		killProcess()
		grammar.unload()
		grammar = None
