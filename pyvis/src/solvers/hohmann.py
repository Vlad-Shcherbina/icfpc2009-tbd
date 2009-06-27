from vm import VM
import sys
from math import sqrt
import hohmann_transfer as ht
import itertools

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

#def fuelForSteps(r1, r2, k):
#    """ The amount of fuel needed to go from r1 to r2 in k equal jumps. """
#    d = (r2 - r1) / k
#    return sum(ht.fuelRequired(r1 + d*i, r1 + d*(i+1)) for i in xrange(0, k))

def steppingTransfers(vm, r2):
    fuel = vm.outPort[1]
    r1 = sqrt(vm.stats.sx**2 + vm.stats.sy**2)
    
    k = 3
        
    d = (r2 - r1) / k
    print r1, d, r1 + d
    for i in xrange(0, k):
        r = sqrt(vm.stats.sx**2 + vm.stats.sy**2)
        rnext = r1 + d * (i+1)
        yield (r, rnext)
            

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
    
    #trans = ht.transfer(r1, r2)

    #while vm.outPort[0] == 0.0:
    #    printStats(vm)
    #    trans.step(vm)
    #    vm.execute()
    
    print "A journey from %f to %f" % (r1, r2)
    for (rstart, rend) in steppingTransfers(vm, r2):
        print "Jump", (rstart, rend)
        trans = ht.transfer(rstart, rend)
        completed = 0
        while completed == 0:
            printStats(vm)
            completed = trans.step(vm)
            vm.execute()
            
    while vm.outPort[0] == 0.0:
            #printStats(vm)
            vm.execute()
        

    print vm.outPort[0]

