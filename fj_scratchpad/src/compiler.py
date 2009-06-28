import distutils
from distutils.core import setup, Extension
from ctypes import *
import platform
import shutil

def build(target):
    # add switches for your arch/os/compiler
    compiler_args = []
    bits = platform.architecture()[0]
    system = platform.system()
    if system == 'Windows' and bits == 32:
        compiler_args.append('/arch:SSE2')
    
    ext = Extension(
                   'compiled_vm', 
                   ['compiled_vm.c'],
                   extra_compile_args = compiler_args,
                   depends = ['compiled_vm_declarations.inc', 'compiled_vm_statements.inc'])
 
    setup(name = 'compiled vm module',
          version = '1.0',
          ext_modules = [ext],
          script_args = ['build_ext', '--inplace'])
    shutil.copy('compiled_vm.pyd', target)

def savefiles(declarations, statements):
    open('compiled_vm_declarations.inc', 'w').write(declarations)
    open('compiled_vm_statements.inc', 'w').write(statements)

class vmwrapper(object):
    def __init__(self, target, vm_desc):
        self.lib = cdll.LoadLibrary(target)
        self.rawrun = getattr(self.lib, "run")
        self.memory_type = c_double * vm_desc.memorysize
        self.output_type = c_double * vm_desc.outputsize
        self.output = self.output_type()
        
        self.rawrun.restype = c_int
        self.rawrun.argtypes = [c_int, c_double, c_double, c_double, 
                                self.memory_type, self.output_type]
        
    def run(self, steps, i2, i3, i16000, memory):
        return self.rawrun(steps, i2, i3, i16000, memory, self.output)
    
    def newmemory(self, iter = None):
        return self.memory_type(*iter)
    
    def clonememory(self, memory):
        res = self.memory_type()
        memmove(res, memory, len(res) * 8)
   
