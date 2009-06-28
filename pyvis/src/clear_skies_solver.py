import sys
from math import *
from random import random
from pprint import pprint

from vminterface import createScenario,getSolution

from compiled_vm import CompiledVMConstructor
from python_vm import PythonVMConstructor 

#vmctr = CompiledVMConstructor
vmctr = PythonVMConstructor

from improver import *

if __name__ == '__main__':
    
    scenario = 4001
    vm = createScenario(vmctr,"../../task/bin4.obf",scenario)
    print 'fuel',vm.state.fuel
    print 'fuel2',vm.state.fuel2
    
    backup = vm.clone()
    
    vm.run(1, 1000.0)
    print vm.state.objects[0]
    print vm.state.objects[2+11]
    print vm.state.collected[11]

    vm.run(5)
    print vm.state.objects[0]
    print vm.state.objects[2+11]
    print vm.state.collected[11]
    
    vm = backup

    vm.executeSteps(1, {1 : (1000.0, 0.0)})
    print vm.state.objects[0]
    print vm.state.objects[2+11]
    print vm.state.collected[11]

    vm.executeSteps(5)
    print vm.state.objects[0]
    print vm.state.objects[2+11]
    print vm.state.collected[11]
