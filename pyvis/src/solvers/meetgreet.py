from vm import VM
import sys
from math import sqrt
from math import atan2
import hohmann_transfer as ht
import orbital as o

def printStats(vm):
    #print "Fuel: %f; Self: %s; Target: %s" % (vm.outPort[1],  str(selfCoords(vm)), str(targetCoords(vm)))
    sx = selfCoords(vm)[0]
    sy = selfCoords(vm)[1]
    tx = targetCoords(vm)[0]
    ty = targetCoords(vm)[1]
    sR = sqrt(sx**2+sy**2)
    tR = sqrt(tx**2+ty**2)
    sa = atan2(sy,sx)
    ta = atan2(ty,tx)
    print "Fuel: %f; Self: R: %s a: %s; Target R: %s a:%s" % (vm.outPort[1], sR, sa, tR, ta) 
def selfCoords(vm):     # >>>>> move this into the vm class later
    return (vm.stats.sx, vm.stats.sy)

def targetCoords(vm):
    sxt, syt = vm.outPort[4], vm.outPort[5]
    return (vm.stats.sx - sxt, vm.stats.sy - syt)

def projectedDistance(sx, sy, tx, ty, tspin):
    """ How far away from target we will end up if we transfer now. """
    r1 = sqrt(sx**2 + sy**2)
    r2 = sqrt(tx**2 + ty**2)
    t = ht.timeRequired(r1, r2)
    txnew, tynew = o.newPosition(tx, ty, tspin, t)
    sxnew, synew = ht.predictPosition(sx, sy, r2)
    
    return sqrt((sxnew - txnew)**2 + (synew - tynew)**2)
    
if __name__ == '__main__':
    assert len(sys.argv) == 2
    assert 1 <= int(sys.argv[1]) <= 4

    with open("../../../task/bin2.obf","rb") as fin:
        data = fin.read()
        
    vm = VM(data)
    vm.setScenario(2000.0 + int(sys.argv[1]))

    vm.execute()
    
    # gather observational data
    sx1, sy1 = selfCoords(vm)
    tx1, ty1 = targetCoords(vm)

    r1 = sqrt(sx1**2 + sy1**2)
    r2 = sqrt(tx1**2 + ty1**2)
    
    vm.execute()
    
    sx2, sy2 = selfCoords(vm)
    tx2, ty2 = targetCoords(vm)
    
    sspin = o.getSpin(sx1, sy1, sx2, sy2)
    tspin = o.getSpin(tx1, ty1, tx2, ty2)
    
    assert (sspin == tspin)     # fuck me if I know how to solve this otherwise
    
    while vm.outPort[0] == 0.0:
        printStats(vm)
        sx, sy = selfCoords(vm)
        tx, ty = targetCoords(vm)
        prsx, prsy = ht.predictPosition(sx, sy, r2)
        t = ht.timeRequired(r1, r2)
        
        if projectedDistance(sx, sy, tx, ty, tspin) < 1000:
            break
        
        vm.execute()

    trans = ht.transfer(r1, r2, sspin)

    while vm.outPort[0] == 0.0:
        printStats(vm)
        trans.step(vm)
        vm.execute()

    print vm.outPort[0]

