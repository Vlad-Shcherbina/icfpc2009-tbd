from __future__ import with_statement

import decompiler
#import decompiler_simple as decompiler
import compiler
import time
import os.path
import inspect
from contextlib import contextmanager
from copy import copy, deepcopy

class CompiledVM(object):
    def __init__(self, parent, scenario, state = None):
        self.parent = parent
        self.vmwrapper = parent.vmwrapper
        self.vm_desc = parent.vm_desc
        if state is None:
            state = self.vmwrapper.newstate(self.vm_desc.memory)
        self.memory, self.output = state
        self.scenario = scenario
    
    def run(self, steps = 1, ax = 0.0, ay = 0.0):
        return self.vmwrapper.run(steps, ax, ay, self.scenario, self.memory, self.output)

    def getoutput(self):
        return self.output

    def clearoutput(self):
        self.output.clear()
    
    
    def reset(self):
        self.memory[:] = self.vm_desc.memory
        self.output.clear()
    
    def print_memory_map(self):
        for i, d in zip(self.vm_desc.memorymap, self.memory):
            print "%04d: %f" % (i, d)
            
    def __copy__(self):
        return self.clone()
    
    def __deepcopy__(self, d):
        return self.clone() # because that's how deep it ever gets!

    def clone(self):
        state = self.vmwrapper.clonestate(self.memory, self.output)
        return CompiledVM(self.parent, self.scenario, state)
        
@contextmanager
def changedir(dir = None, file = None):
    if file:
        assert dir is None
        dir = os.path.dirname(file)
    save = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(save)
                


class CompiledVMConstructor(object):
    def __init__(self, filename,sliced=False):
        vm_name = 'cvm_' + os.path.splitext(os.path.basename(filename))[0]
        if sliced:
            vm_name += '_sliced'
        vm_name += '.pyd'
        print 'Constructing VM for "' + filename + '" as ' + vm_name
        if sliced:
            self.vm_desc = vm_desc = decompiler.process_file(filename,interestingPorts=[0x02,0x03])
        else:
            self.vm_desc = vm_desc = decompiler.process_file(filename)
        sourcetime = os.path.getmtime(filename)
        
        with changedir(file = __file__):
            compiler.savefiles(vm_desc.declarations, vm_desc.statements)
            rebuild = True
            if os.path.exists(vm_name):
                filetime = os.path.getmtime(vm_name)
                sources = [inspect.getsourcefile(CompiledVMConstructor),
                           inspect.getsourcefile(compiler),
                           inspect.getsourcefile(decompiler),
                           inspect.getsourcefile(decompiler.asm),
                           'compiled_vm.c']
                sourcetime = max([os.path.getmtime(s) for s in sources] + [sourcetime])  
                if sourcetime < filetime:
                    #print 'Skipping rebuild'
                    rebuild = False
            if rebuild: compiler.build(vm_name)
            self.vmwrapper = compiler.vmwrapper(vm_name, vm_desc)
        
    def newvm(self, scenario):
        return CompiledVM(self, scenario)



if __name__ == '__main__':
    
    obf = '../../../task/bin4.obf'
    scenario = 4001.0
    steps = 2000000
    
    print 'full version'
    constructor = CompiledVMConstructor(obf)
    vm = constructor.newvm(scenario)
    print 'memory size:',vm.vm_desc.memorysize
    clock = time.clock()
    print vm.run(steps, 0, 0)
    print time.clock() - clock
    print list(vm.output)
    #vm.print_memory_map()
    
    print
    print 'sliced version'
    constructor = CompiledVMConstructor(obf,sliced=True)
    vm = constructor.newvm(scenario)
    print 'memory size:',vm.vm_desc.memorysize
    clock = time.clock()
    print vm.run(steps, 0, 0)
    print time.clock() - clock
    print list(vm.output)
    #vm.print_memory_map()
    
    