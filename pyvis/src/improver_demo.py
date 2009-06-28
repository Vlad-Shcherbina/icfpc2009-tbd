import psyco
psyco.full()

from copy import deepcopy
import sys

from vminterface import createScenario,getSolution

from compiled_vm import CompiledVMConstructor
from python_vm import PythonVMConstructor 

vmctr = CompiledVMConstructor
#vmctr = PythonVMConstructor

from improver import *

#def compare(vm):

if __name__ == '__main__':
    
    scenario = 2002
    vmP = createScenario(vmctr,"../../task/bin2.obf",scenario)
    
    vm = vmP
    vm0 = vm.clone()
    
    controls = {}
    controls =\
        {50093: [-586.12604983102585, -2082.2600164696337],
         84624: [341.59587795921209, 1212.8699666971638]}    
    expectedTime = 84624
    variationPoints = [50000,expectedTime]
    
    print 'initial badness',calcBadness(vm,1,controls,
                                      expectedTime,expectedTime+900)
    
    controls = improveMeetAndGreet(vm,1,controls,variationPoints,
                                   expectedTime,expectedTime+900)

#    controls = tryImprove(vm,1,controls,variationPoints,
#                          expectedTime,expectedTime+900)
        
    print 'final badness',calcBadness(vm,1,controls,
                                      expectedTime,expectedTime+900)

    print sorted(controls.items())
    
    vm = vm0
    print 'checking improved version'
    steps = vm.executeSteps(3000000,controls)
    
    print 'SCORE',vm.state.score
    with open('improved_sol','wb') as fout:
        fout.write(getSolution(scenario,vm.state.time,controls))
        
    