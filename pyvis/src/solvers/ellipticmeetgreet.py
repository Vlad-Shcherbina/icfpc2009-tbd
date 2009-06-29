from __future__ import with_statement

import sys
from math import sqrt, atan2, pi
import time

import vm as VM
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

if __name__ == '__main__':
    assert len(sys.argv) == 2
    assert 1 <= int(sys.argv[1]) <= 4

    scenario = 3000 + int(sys.argv[1])    
    vm = VM.createScenario("../../../task/bin3.obf", scenario)

    pos1 = vm.state.objects[0]
    vm.executeSteps(1, {})
    pos2 = vm.state.objects[0]
    (x1,y1), (x2,y2) = pos1, pos2
    
    v = o.vLen(o.vDiff(pos2, pos1))
    r1 = o.vLen(pos1)
    r2 = o.vLen(pos1)
    
    a = 1/(2/r1 - v**2/o.mu)
    
    
    print (x1, y1, abs(2*a - r1)), (x2, y2, abs(2*a - r2))
    
    
    # one of those is the other focus of the orbit, which is shown in the cycle below
    focus1, focus2 = o.circleIntersection((x1, y1, abs(2*a - r1)), \
                                          (x2, y2, abs(2*a - r2)))
    
    print focus1, focus2
    
    while True:
        pos = vm.state.objects[0]
        sum1 = o.vLen(pos) + o.vLen(o.vDiff(pos, focus1))
        sum2 = o.vLen(pos) + o.vLen(o.vDiff(pos, focus2))
        print sum1, sum2
        vm.executeSteps(1, {})
           
    
