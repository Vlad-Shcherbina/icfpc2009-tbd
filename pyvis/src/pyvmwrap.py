
from orbitvm import OrbitVM
from pyvm import VM

class PyVM(OrbitVM):
	def __init__(self, data, type, config):
		self.vm = VM(data)
		OrbitVM.__init__(self, type, config)
		return
	
	def run(self):
		return
	
	def readport(self, port):
		return self.vm.outPort[port]
	
	def writeport(self, port, val):
		self.vm.inPort[port] = val
	
	def gettime(self):
		return self.t
	
	def nextStep(self):
		self.t = self.t+1
		self.vm.execute()
		self.vm.printStats()
