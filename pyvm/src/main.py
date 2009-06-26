import sys
import os

from vm import VM                
                
if __name__ == '__main__':
    assert len(sys.argv) == 2
    print os.getcwd()
    with open(sys.argv[1],"rb") as fin:
        data = fin.read()
        
    vm = VM(data)
    vm.inPort[0x3E80] = 1001.0
    while vm.outPort[0] == 0.0:
        vm.printStats()
        print 'step'
        vm.execute()
        vm.memDump()
        break
        vm.printStats()
    
    
    
    print 'ok'