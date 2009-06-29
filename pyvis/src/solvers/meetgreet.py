from __future__ import with_statement

import sys
from math import sqrt, atan2, pi
import time

import vm as VM
import hohmann_transfer as ht
import orbital as o

def printStats(vm):
    #print "Fuel: %f; Self: %s; Target: %s" % (vm.outPort[1],  str(selfCoords(vm)), str(targetCoords(vm)))
    sx, sy = vm.state.objects[0]
    tx, ty = vm.state.objects[1]
    tR = o.vLen((tx, ty))
    sa = atan2(sy,sx)/pi
    ta = atan2(ty,tx)/pi
    dist = o.vLen((sx-tx, sy-ty))
    print "Fuel: %f; Self: R: %s a: %s; Target R: %s a:%s; Dist: %s" % (vm.state.fuel, vm.state.r, sa, tR, ta, dist) 

def projectedDistance(sx, sy, tx, ty, tspin):
    """ How far away from target we will end up if we transfer now. """
    r1 = o.vLen((sx, sy))
    r2 = o.vLen((tx, ty))
    t = ht.timeRequired(r1, r2)
    txnew, tynew = o.newPosition(tx, ty, tspin, t)
    sxnew, synew = ht.predictPosition(sx, sy, r2)
    
    return o.vLen((sxnew - txnew, synew-tynew))
    
def obtainSpins(vm):
    sx1, sy1 = vm.state.objects[0]
    tx1, ty1 = vm.state.objects[1]

    vm.executeSteps(1, {})
    
    sx2, sy2 = vm.state.objects[0]
    tx2, ty2 = vm.state.objects[1]
    
    sspin = o.getSpin(sx1, sy1, sx2, sy2)
    tspin = o.getSpin(tx1, ty1, tx2, ty2)
    return (sspin, tspin)

if __name__ == '__main__':
    assert len(sys.argv) == 2
    assert 1 <= int(sys.argv[1]) <= 4

    scenario = 2000 + int(sys.argv[1])    
    vm = VM.createScenario("../../../task/bin2.obf", scenario)
 
    # gather observational data
    sspin, tspin = obtainSpins(vm)
    r1 = vm.state.r
    r2 = o.vLen(vm.state.objects[1])
    
    assert (sspin == tspin)     # fuck me if I know how to solve this otherwise
    
    while vm.state.score == 0.0:
        sx, sy = vm.state.objects[0]
        tx, ty = vm.state.objects[1]
        prsx, prsy = ht.predictPosition(sx, sy, r2)
        t = ht.timeRequired(r1, r2)
        
        if projectedDistance(sx, sy, tx, ty, tspin) < 1000:
            break
        
        vm.executeSteps(1,{})

    ht.performTransfer(vm, r2, sspin)

    while vm.state.score == 0.0:
        vm.execute()

    print vm.state.score
    
    with open('../solutions/sol_' + str(scenario),'wb') as fout:
        fout.write(vm.getSolution())
    
class MeetGreetController:
    def __init__(self, vm):
        self.vm = vm
        
        vm.execute()
        self.sx1, self.sy1 = vm.state.objects[0]
        self.tx1, self.ty1 = vm.state.objects[1]
        self.r1 = vm.state.r
        self.r2 = sqrt(self.tx1**2 + self.ty1**2)
        self.state = 1
        
    def step(self):
        vm = self.vm
        if self.state == 1:
            self.state=2
            pass
        if self.state == 2:
            self.sx2, self.sy2 = vm.state.objects[0]
            self.tx2, self.ty2 = vm.state.objects[1]
    
            self.sspin = o.getSpin(self.sx1, self.sy1, self.sx2, self.sy2)
            self.tspin = o.getSpin(self.tx1, self.ty1, self.tx2, self.ty2)
    
            #assert (self.sspin == self.tspin)     # fuck me if I know how to solve this otherwise
            self.state = 3
            pass
        if self.state == 3:
            #printStats(vm)
            sx, sy = vm.state.objects[0]
            tx, ty = vm.state.objects[1]
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


class MeetGreetLasyController:
    """
    Does hohmann on a first step, then uses hohmanns to correct
    orbit and 'await' for the sattelite on the same orbit
    """
    def __init__(self, vm):
        self.vm = vm
        vm.execute()
        self.calcData()
        self.state = 'init'
        
    def calcData(self):
        self.sx1, self.sy1 = self.vm.state.objects[0]
        self.tx1, self.ty1 = self.vm.state.objects[1]
        self.r1 = self.vm.state.r
        self.r2 = o.vLen(self.vm.state.objects[1])
        self.diff = sqrt( (self.sx1-self.tx1)**2 + (self.sy1-self.ty1)**2)
        self.a1 = o.vAngle(self.vm.state.objects[0])
        self.a2 = o.vAngle(self.vm.state.objects[1])
        # da determines either to wait and slowdown or to speedup
        self.da = self.a1 - self.a2
        if (self.da > pi):
            self.da = self.da - 2*pi
                    
    def step(self):
        vm = self.vm
        self.calcData()
        
        if self.state == 'init':
            self.trans = ht.transfer(self.r1, self.r2)
            self.state = 'do_hohmann'
        
        if self.state == 'do_hohmann':
            spin = self.trans.step(vm)
            if spin != 0:
                self.state = 'positioned'
                pass
            
        if self.state == 'positioned':
            # slowing down or fastening
            if self.diff > 1000:
                if self.da < 0:
                    self.r2 = self.r1 + self.diff/5
                else:
                    self.r2 = self.r1 - self.diff/5
                self.trans = ht.transfer(self.r1, self.r2)
                self.state = 'await'
                pass

        if self.state == 'await':
            spin = self.trans.step(vm)
            if spin != 0:
                self.trans = ht.transfer(self.r1, self.r2)
                self.state = 'do_hohmann'
                pass
            
    def draw(self, vis):
        vis.drawText("state:%s\n r1:%f\n r2:%f\n diff:%f\n a1:%f,a2:%f,da:%f"\
                 %(self.state, self.r1, self.r2, self.diff,
                   self.a1, self.a2, self.da),
                 0, 120, 100, 100)
        pass
                
