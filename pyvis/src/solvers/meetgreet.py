from vm import VM
import sys
from math import sqrt
from math import atan2
import hohmann_transfer as ht
import orbital as o
import time
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
    dist = sqrt((sx-tx)**2+(sy-ty)**2)
    print "Fuel: %f; Self: R: %s a: %s; Target R: %s a:%s; Dist: %s" % (vm.outPort[1], sR, sa, tR, ta, dist) 
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

    fin - open("../../../task/bin2.obf","rb")
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
        #printStats(vm)
        sx, sy = selfCoords(vm)
        tx, ty = targetCoords(vm)
        prsx, prsy = ht.predictPosition(sx, sy, r2)
        t = ht.timeRequired(r1, r2)
        
        if projectedDistance(sx, sy, tx, ty, tspin) < 1000:
            break
        
        vm.execute()

    printStats(vm)
    print prsx, prsy
    trans = ht.transfer(r1, r2, sspin)

    while vm.outPort[0] == 0.0:
        printStats(vm)
        trans.step(vm)
        vm.execute()

    print vm.outPort[0]
    
class MeetGreetController:
    def __init__(self, vm):
        self.vm = vm
        
        vm.execute()
        self.sx1, self.sy1 = selfCoords(vm)
        self.tx1, self.ty1 = targetCoords(vm)
        self.r1 = sqrt(self.sx1**2 + self.sy1**2)
        self.r2 = sqrt(self.tx1**2 + self.ty1**2)
        self.state = 1
        
    def step(self):
        vm = self.vm
        if self.state == 1:
            self.state=2
            pass
        if self.state == 2:
            self.sx2, self.sy2 = selfCoords(vm)
            self.tx2, self.ty2 = targetCoords(vm)
    
            self.sspin = o.getSpin(self.sx1, self.sy1, self.sx2, self.sy2)
            self.tspin = o.getSpin(self.tx1, self.ty1, self.tx2, self.ty2)
    
            #assert (self.sspin == self.tspin)     # fuck me if I know how to solve this otherwise
            self.state = 3
            pass
        if self.state == 3:
            #printStats(vm)
            sx, sy = selfCoords(vm)
            tx, ty = targetCoords(vm)
            prsx, prsy = ht.predictPosition(sx, sy, self.r2)
            t = ht.timeRequired(self.r1, self.r2)
        
            if projectedDistance(sx, sy, tx, ty, self.tspin) < 1000:
                self.state = 4
                pass
            #time.sleep(0.000001)
            pass
        if self.state == 4:
            self.trans = ht.transfer(self.r1, self.r2, self.sspin)
            self.state = 5
            self.s5timer = 0
        
        if self.state == 5:
            self.trans.step(vm)
            #time.sleep(0.001)
            pass
 