from vm import VM
import sys
from math import sqrt
from hohmann_transfer import transfer

def printStats(vm):
    sx, sy = vm.stats.sx, vm.stats.sy
    print "Fuel: %f; Rcurrent: %f; Rdest: %f" % (vm.outPort[1],  sqrt(sx**2 + sy**2), vm.outPort[4])

class HohmannController:
    def __init__(self, vm):
        self.vm = vm
        vm.execute()
        r1 = sqrt(vm.stats.sx**2 + vm.stats.sy**2)
        r2 = vm.outPort[4]
        self.trans = transfer(r1, r2)
        
    def step(self):
        self.trans.step(self.vm)

if __name__ == '__main__':
    assert len(sys.argv) == 2
    assert 1 <= int(sys.argv[1]) <= 4

    fin = open("../../../task/bin1.obf","rb")
    data = fin.read()
        
    vm = VM(data)
    vm.setScenario(1000.0 + int(sys.argv[1]))
    
    vm.execute()    # please don't remove this line again

    r1 = sqrt(vm.stats.sx**2 + vm.stats.sy**2)
    r2 = vm.outPort[4]
    
    trans = transfer(r1, r2)

    while vm.outPort[0] == 0.0:
        printStats(vm)
        trans.step(vm)
        vm.execute()

    print vm.outPort[0]

