from __future__ import with_statement
import sys
import struct
from pprint import pprint

from vm import teamID,createScenario,getSolution

from compiled_vm import CompiledVMConstructor
from python_vm import PythonVMConstructor 


if __name__ == '__main__':
    ctors = {
            'compiled': CompiledVMConstructor, 
            'python': PythonVMConstructor,
            }
    assert len(sys.argv) == 4, "specify vm ({0}), .obf file and solution file".format(
        ", ".join(ctors.keys()))
    
    with open(sys.argv[3],"rb") as fin:
        sol = fin.read()
    
    (signature,tid,scenario) = struct.unpack('<III',sol[:12])
    assert signature == 0xCAFEBABE
    assert tid == teamID
    
    print 'scenario', scenario
    
    vm = createScenario(ctors[sys.argv[1]], sys.argv[2], scenario)
    assert vm.state.time == 1 # because 0 is initializing iteration
    
    controls = {}
    
    i = 12
    while i < len(sol):
        timeStamp,numWrites = struct.unpack('<II',sol[i:i+8])
        i += 8
        controls[timeStamp] = [0.0,0.0]
        for j in range(numWrites):
            addr,value = struct.unpack("<Id",sol[i:i+12])
            i += 12
            if timeStamp>0:
                if addr == 2:
                    controls[timeStamp][0] = value
                elif addr == 3:
                    controls[timeStamp][1] = value
            else:
                assert addr == 16000 and value == float(scenario)
        
    if numWrites != 0:
        print 'Solution file corrupted. '
        print 'Probably you ignored nonpositive score warning when saving this solution'
    
    controls = dict((k,v) for k,v in controls.items())
    print 'controls =\\'
    pprint(controls)

    # because we already were on step 1 after createScenario
    steps = vm.executeSteps(timeStamp-1, controls) + 1
    
    if steps != timeStamp:
        print "The machine aborted prematurely after {0} steps!".format(steps) 
    print 'SCORE IS',vm.state.score
    
    
