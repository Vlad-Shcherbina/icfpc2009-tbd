

class OrbitVM():

	Hohmann    = 1000
	MeetnGreet = 2000
	Eccentric  = 3000
	ClearSkies = 4000
	
	EarthRadius = 6.357e6
	
	t = 0

	def __init__(self, type, config):
		self.type = type
		self.config = config
		return
	
	def gettype(self):
		return self.type
	
	def terminate(self):
		return

	def readport(self, port):
		return 0
	
	def writeport(self, port, val):
		return 0
	
	def gettime(self):
		return self.t
	
	def step(self):
		self.t = self.t+1
		
class DummyVM(OrbitVM):

	def __init__(self, type, config):
		OrbitVM.__init__(self, type, config)
		return
			
	def readport(self, port):
		return port*10e4-self.t*1000
	
	def writeport(self, port, val):
		return 0
	
	def step(self):
		self.t = self.t+1
	