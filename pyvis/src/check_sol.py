from __future__ import with_statement
import sys
import struct
from pprint import pprint

from vm import VM,teamID


if __name__ == '__main__':
    assert len(sys.argv) == 3, "specify .obf file and solution file"
    
    with open(sys.argv[1],"rb") as fin:
        data = fin.read()
    vm = VM(data)
    
    with open(sys.argv[2],"rb") as fin:
        sol = fin.read()
    
    (signature,tid,scenario) = struct.unpack('<III',sol[:12])
    assert signature == 0xCAFEBABE
    assert tid == teamID
    
    vm.setScenario(scenario)
    print 'scenario',scenario
    
    step = 0

    i = 12
    
    controls = {}
    
    while i < len(sol):
        timeStamp,numWrites = struct.unpack('<II',sol[i:i+8])
        i += 8
        while step < timeStamp:
            assert step == 0 or vm.state.score == 0.0
            vm.execute()
            step += 1
        print timeStamp,numWrites
        controls[timeStamp] = [0.0,0.0]
        for j in range(numWrites):
            addr,value = struct.unpack("<Id",sol[i:i+12])
            i += 12
            print 'write port',addr,value
            if timeStamp>0:
                if addr == 1:
                    controls[timeStamp][0] += value
                elif addr == 2:
                    controls[timeStamp][1] += value
            vm.writePort(addr,value) 
            # bug here if you keep same nonzero speed for two steps!
        
    assert numWrites == 0
    
    controls = dict((k,v) for k,v in controls.items() if v!=[0.0,0.0])
    print 'controls =\\'
    pprint(controls)
    
    
    print 'SCORE IS',vm.state.score

    assert sol == vm.getSolution()
    
