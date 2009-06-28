from copy import deepcopy
import sys

from vm import *
from improver import *

if __name__ == '__main__':
    
    vm = createScenario("../../task/bin2.obf",2002)
    vm0 = vm.clone()
    
    controls = {}
    controls =\
        {50093: [-586.12604983102585, -2082.2600164696337],
         84624: [341.59587795921209, 1212.8699666971638]}    
    expectedTime = 84624
    variationPoints = [50000,expectedTime]
    
    for i in range(1):
        controls = improveMeetAndGreet(vm,1,controls,variationPoints,
                                       expectedTime,expectedTime+900)
        
    print 'final badness',calcBadness(vm,1,controls,
                                      expectedTime,expectedTime+900)

    print sorted(controls.items())
    
    vm = vm0
    print 'checking improved version'
    while vm.state.score == 0.0 and vm.state.time < 100000:
        #print vm.state.time
        if vm.state.time in controls:
            vm.changeSpeed(*controls[vm.state.time])
        vm.execute()
        
    print 'SCORE',vm.state.score
    with open('improved_sol','wb') as fout:
        fout.write(vm.getSolution())
        
    