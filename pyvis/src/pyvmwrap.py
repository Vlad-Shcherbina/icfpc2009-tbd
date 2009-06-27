
from orbitvm import OrbitVM
from vm import VM
import time


class PyVM(OrbitVM):
	def __init__(self, data, type, config):
		self.vm = VM(data)
		OrbitVM.__init__(self, type, config)
		self.vm.setScenario(self.type+self.config)
		return
	
	def getVMImpl(self):
		return self.vm
	
	def readport(self, port):
		return self.vm.outPort[port]
	
	def writeport(self, port, val):
		self.vm.inPort[port] = val
	
	def gettime(self):
		return self.t
	
	def step(self):
		self.t = self.t+1
		self.vm.execute()
		#self.vm.printStats()
