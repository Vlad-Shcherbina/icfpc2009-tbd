import decompiler
import compiler
import time
import os.path
import inspect

class CompiledVM(object):
    def __init__(self, parent, scenario, memory = None):
        self.parent = parent
        self.vmwrapper = parent.vmwrapper
        self.vm_desc = parent.vm_desc
        if memory is None:
            memory = self.vmwrapper.newmemory(self.vm_desc.memory)
        self.memory = memory
        self.scenario = scenario
    
    def run(self, steps, ax, ay):
        return self.vmwrapper.run(steps, ax, ay, self.scenario, self.memory)
    
    def reset(self):
        self.memory[:] = self.vm_desc.memory
    
    def print_memory_map(self):
        for i, d in zip(self.vm_desc.memorymap, self.memory):
            print "%04d: %f" % (i, d)
            
    def __copy__(self):
        newmem = self.vmwrapper.clonememory(self.memory)
        return CompiledVM(self.parent, self.scenario, newmem)
    
    def __deepcopy__(self, d):
        return self.__copy__() # because that's how deep it gets!
         
        
            

class CompiledVMConstructor(object):
    def __init__(self, filename):
        vm_name = 'cvm_' + os.path.splitext(os.path.basename(filename))[0] + '.pyd'
        print 'Constructing VM for "' + filename + '" as ' + vm_name
        self.vm_desc = vm_desc = decompiler.process_file(filename)
        compiler.savefiles(vm_desc.declarations, vm_desc.statements)
        
        rebuild = True
        if os.path.exists(vm_name):
            filetime = os.path.getmtime(vm_name)
            sources = [inspect.getsourcefile(CompiledVMConstructor),
                       inspect.getsourcefile(compiler),
                       inspect.getsourcefile(decompiler),
                       inspect.getsourcefile(decompiler.asm),
                       filename]
            sourcetime = max(os.path.getmtime(s) for s in sources if s)
            if sourcetime < filetime:
                print 'Skipping rebuild'
                rebuild = False
        if rebuild: compiler.build(vm_name)
        self.vmwrapper = compiler.vmwrapper(vm_name, vm_desc)
        
    def newvm(self, scenario):
        return CompiledVM(self, scenario)



if __name__ == '__main__':
    constructor = CompiledVMConstructor('../../task/bin4.obf')
    vm = constructor.newvm(4001.0)
    
    clock = time.clock()   
    print vm.run(3000000, 0, 0)
    print time.clock() - clock
    print list(vm.vmwrapper.output)
    vm.print_memory_map()
    
    
    