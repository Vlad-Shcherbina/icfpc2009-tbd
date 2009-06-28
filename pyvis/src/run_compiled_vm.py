from compiled_vm import CompiledVMConstructor
import time

if __name__ == '__main__':
    constructor = CompiledVMConstructor('../../task/bin2.obf')
    vm = constructor.newvm(1001.0)
    
    clock = time.clock()   
    print vm.run(3000000, 0, 0)
    print time.clock() - clock
    print list(vm.vmwrapper.output)
    vm.print_memory_map()
