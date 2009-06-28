from __future__ import with_statement
import sys
import struct
from pprint import pprint

from vm import teamID,createScenario


if __name__ == '__main__':
    assert len(sys.argv) == 3, "specify .obf file and solution file"
    
    with open(sys.argv[2],"rb") as fin:
        sol = fin.read()
    
    (signature,tid,scenario) = struct.unpack('<III',sol[:12])
    assert signature == 0xCAFEBABE
    assert tid == teamID
    
    print 'scenario',scenario
    
    vm = createScenario(sys.argv[1],scenario)
    assert vm.state.time == 1 # because 0 is initializing iteration
    
    vmClone = vm.clone()

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
                    controls[timeStamp][0] += value
                elif addr == 3:
                    controls[timeStamp][1] += value
            else:
                assert addr == 0x3E80 and value == float(scenario)
        
    if numWrites != 0:
        print 'Solution file corrupted. '
        print 'Probably you ignored nonpositive score warning when saving this solution'
    
    controls = dict((k,v) for k,v in controls.items() if v!=[0.0,0.0])
    print 'controls =\\'
    pprint(controls)

    # because we already were on step 1 after createScenario
    vm.executeSteps(timeStamp-1,controls)
    
    print 'SCORE IS',vm.state.score

    assert sol == vm.getSolution()
    
