import distutils
from distutils.core import setup, Extension
import distutils.dir_util
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
    
    distutils.dir_util._path_created = {} # because of bug in dir_util! fuck'em
    setup(name = 'compiled vm module',
          version = '1.0',
          ext_modules = [ext],
          script_args = ['build_ext', '--inplace'])
    
    shutil.move('compiled_vm.pyd', target)
    shutil.rmtree('build')
    # to prevent setup from using result of compilation that happens 0.000001 seconds
    # before, but for different machine.
    # (and aslo to make this dir look cleaner)

def savefiles(declarations, statements):
    open('compiled_vm_declarations.inc', 'w').write(declarations)
    open('compiled_vm_statements.inc', 'w').write(statements)

class vmwrapper(object):
    def __init__(self, target, vm_desc):
        self.lib = cdll.LoadLibrary(target)
        self.rawrun = getattr(self.lib, "run")
        self.memory_type = c_double * vm_desc.memorysize
        self.output_type = c_double * vm_desc.outputsize
        
        self.rawrun.restype = c_int
        self.rawrun.argtypes = [c_int, c_double, c_double, c_double, 
                                self.memory_type, self.output_type]
        
    def run(self, steps, i2, i3, i16000, memory, output):
        return self.rawrun(steps, i2, i3, i16000, memory, output)
    
    def newstate(self, iter = None):
        return (self.memory_type(*iter), self.output_type())
    
    def clonestate(self, memory, output):
        mem = self.memory_type()
        memmove(mem, memory, len(mem) * 8)
        out = self.output_type()
        memmove(out, output, len(out) * 8)
        return (mem, out)
