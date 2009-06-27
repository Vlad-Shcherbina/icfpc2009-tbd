import decompiler
import compiler

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
        self.vmwrapper.run(steps, ax, ay, self.scenario, self.memory)
        
            

class CompiledVMConstructor(object):
    def __init__(self, filename):
        print 'Constructing VM for', filename
        self.vm_desc = vm_desc = decompiler.process_file(filename)
        compiler.savefiles(vm_desc.declarations, vm_desc.statements)
        compiler.build()
        self.vmwrapper = compiler.vmwrapper(vm_desc)
        
    def newvm(self, scenario):
        return CompiledVM(self, scenario)
          
        
 




if __name__ == '__main__':
    constructor = CompiledVMConstructor('../../task/bin1.obf')
    vm = constructor.newvm(1001.0)
    print vm.run(1, 0, 0)
    print list(vm.vmwrapper.output)
    print list(vm.memory)