import sys
import os

from vm import VM                
                
if __name__ == '__main__':
    assert len(sys.argv) == 2, "specify .obf file"
    with open(sys.argv[1],"rb") as fin:
        data = fin.read()
    vm = VM(data)
    vm.setScenario(1001)
    while vm.stats.score == 0.0:
        print 'step'
        vm.execute()
        vm.changeSpeed(10,12)
        vm.changeSpeed(10,12) # overwrite previous
        #vm.memDump()
        vm.printStats()
        if True:
            vm.execute()
            break # to finish after first iteration
    
    
    with open('solution','w') as fout:
        fout.write(vm.getSolution())
    
    print 'finished'