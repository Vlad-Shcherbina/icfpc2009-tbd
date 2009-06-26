
from orbitvm import OrbitVM
from vm import VM
from threading import Thread
import time


class PyVM(OrbitVM, Thread):
	def __init__(self, data, type, config):
		self.vm = VM(data)
		OrbitVM.__init__(self, type, config)
		self.term = 0
		Thread.__init__(self)
		self.start()
		return
	
	def run(self):
		while not self.term:
			self.nextStep()
			time.sleep(0.000002)
		return

	def terminate(self):
		self.term = 1
		return
	
	def _idle(self):
		1
		#
	
	def readport(self, port):
		return self.vm.outPort[port]
	
	def writeport(self, port, val):
		self.vm.inPort[port] = val
	
	def gettime(self):
		return self.t
	
	def nextStep(self):
		self.t = self.t+1
		self.vm.execute()
		#self.vm.printStats()
