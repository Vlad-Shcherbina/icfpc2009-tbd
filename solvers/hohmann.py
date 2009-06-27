from vm import VM
import sys
from math import sqrt
from hohmann_transfer import transfer

def printStats(vm):
    sx, sy = vm.stats.sx, vm.stats.sy
    print "Fuel: %f; Rcurrent: %f; Rdest: %f" % (vm.outPort[1],  sqrt(sx**2 + sy**2), vm.outPort[4])

if __name__ == '__main__':
    assert len(sys.argv) == 2
    assert 1 <= int(sys.argv[1]) <= 4

    with open("../task/bin1.obf","rb") as fin:
        data = fin.read()
        
    vm = VM(data)
    vm.setScenario(1000.0 + int(sys.argv[1]))

    vm.execute()
    trans = transfer(vm)

    while vm.outPort[0] == 0.0:
        printStats(vm)
        trans.step(vm)
        vm.execute()

    print vm.outPort[0]

