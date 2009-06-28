from vm import VM
import sys
from math import sqrt
import hohmann_transfer as ht
import itertools

def printStats(vm):
    print "Fuel: %f; Rcurrent: %f; Rdest: %f" % (vm.state.fuel,  vm.state.r, vm.state.radius)

####################################################
# HohmannController contains an outdated version of the algorithm
# (run this module directly to get the new one).
# I'm not fixing this until there's a more clear understanding of how
# the solvers interact with the rest of the system.
####################################################
class HohmannController:
    def __init__(self, vm):
        self.vm = vm
        vm.execute()
        self.trans = transfer(vm.state.r, vm.state.radius)
        
    def step(self):
        self.trans.step(self.vm)

def fuelBurnOrbits(r1, r2, fuel):
    """ Find the orbits r3, ..., rk such that going
        r1 -> r3 -> r1 -> r4 -> ... -> r1 -> r2 will
        burn as much fuel as possible. """
    
    fuel -= ht.fuelRequired(r1,r2)
    
    fuelBurn = lambda r3: 2 * ht.fuelRequired(r1, r3)
    
    rmin = r1
    rmax = 15.6 * r1    # this magic number is from wikipedia
    
    while fuelBurn(rmax) < fuel - 10:
        yield rmax
        fuel -= fuelBurn(rmax)
    
    while rmax - rmin > 1:
        r = (rmax + rmin) / 2
        if fuelBurn(r) < fuel:
            rmin = r
        else:
            rmax = r
    
    yield rmin - 100    # leaving a 100m margin to account for discretization errors 

if __name__ == '__main__':
    assert len(sys.argv) == 2
    assert 1 <= int(sys.argv[1]) <= 4

    fin = open("../../../task/bin1.obf","rb")
    data = fin.read()
        
    vm = VM(data)
    vm.setScenario(1000.0 + int(sys.argv[1]))
    
    vm.execute()    # please don't remove this line again

    r1 = vm.state.r
    r2 = vm.state.radius
    
    for r in fuelBurnOrbits(r1, r2, vm.state.fuel):
        ht.transfer(r1, r).performTransfer(vm)
        ht.transfer(r, r1).performTransfer(vm)

    ht.transfer(r1, r2).performTransfer(vm)
    printStats(vm)
    
    while vm.state.score == 0.0:
            vm.execute()

    print vm.state.score
    