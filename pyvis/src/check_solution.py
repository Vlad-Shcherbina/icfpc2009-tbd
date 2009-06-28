from __future__ import with_statement
import sys
import struct
from pprint import pprint

from vminterface import teamID,createScenario,getSolution,parseSolution

from compiled_vm import CompiledVMConstructor
from python_vm import PythonVMConstructor 
ctors = {
        'compiled': CompiledVMConstructor, 
        'python': PythonVMConstructor,
        }

def check_solution(vmtype, vmfile, solutionfile):
    with open(solutionfile, "rb") as fin:
        sol = fin.read()
    
    scenario, controls, numSteps = parseSolution(sol)
    
    print 'scenario', scenario
    print 'numSteps', numSteps 
    print 'controls =\\'
    pprint(controls)
    
    vm = createScenario(ctors[vmtype], vmfile, scenario)
    assert vm.state.time == 1

    # because we already were on step 1 after createScenario
    steps = vm.executeSteps(numSteps - 1, controls) + 1
    
    if steps != numSteps:
        print "The machine aborted prematurely after {0} steps!".format(steps)
        
    print 'SCORE IS',vm.state.score
    
if __name__ == '__main__':
    assert len(sys.argv) == 4, "specify vm ({0}), .obf file and solution file".format(
        ", ".join(ctors.keys()))
    check_solution(sys.argv[1], sys.argv[2], sys.argv[3])
    
    
