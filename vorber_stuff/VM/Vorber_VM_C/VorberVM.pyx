cdef extern from "VM.h":
	ctypedef struct c_VM "VorberVirtualMachine":
		void LoadProgram(char* filename)
		void LoadInputText(char* filename)
		void WriteOutput(char* filename)
		void Reset()
		void Process()
		void Run()
	c_VM *new_VM "new VorberVirtualMachine"()
	void del_VM "delete"(c_VM *vm)
cdef class VM:
	cdef c_VM *instance
	def __cinit__(self):
		self.instance = new_VM()
	def __dealloc__(self):
		del_VM(self.instance)
	def LoadProgram(self, filename):
		self.instance.LoadProgram(filename)
	def LoadInputText(self, filename):
		self.instance.LoadInputText(filename)
	def WriteOutput(self, filename):
		self.instance.WriteOutput(filename)
	def Reset(self):
		self.instance.Reset()
	def Process(self):
		self.instance.Process()
	def Run(self):
		self.instance.Run()
