import sys

from vminterface import createScenario,getSolution

from improver import *

#def compare(vm):

if __name__ == '__main__':
    
    scenario = 2002
    vm = createScenario('compiled',"../../task/bin2.obf",scenario)
    
    vm0 = vm.clone()
    
    print 'fuel',vm.state.fuel
    
    controls = {}
    controls =\
        {50093: [-586.12604983102585, -2082.2600164696337],
         84624: [341.59587795921209, 1212.8699666971638]}
#    controls = {50000:[-700,-1800],
#                84000:[200,1000]}    
    expectedTime = 84624
    variationPoints = [50000,expectedTime]
    
    print 'initial badness',calcBadness(vm,1,controls,
                                      expectedTime,expectedTime+900)
    
#    controls = improveMeetAndGreet(vm,1,controls,variationPoints,
#                                   expectedTime,expectedTime+900)

    controls = tryImprove(vm,1,controls,variationPoints,
                          expectedTime,expectedTime+900)
        
    print 'final badness',calcBadness(vm,1,controls,
                                      expectedTime,expectedTime+900)

    print sorted(controls.items())
    
    vm = vm0
    print 'checking improved version'
    steps = vm.executeSteps(3000000,controls)
    
    print 'SCORE',vm.state.score
    with open('improved_sol','wb') as fout:
        fout.write(getSolution(scenario,vm.state.time,controls))
        
    