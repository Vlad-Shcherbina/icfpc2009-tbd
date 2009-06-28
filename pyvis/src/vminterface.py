from __future__ import with_statement

import psyco
psyco.full()

from copy import copy,deepcopy

import struct
from math import *

__all__ = [
    "teamID",
    "createScenario",
    "getSolution",
]

teamID = 160

class State(object):
    __slots__ = (
        'scenario',
        'time',
        'score',
        'fuel',
        'r', # distance to the center of the earth
        'objects', # list of coordiante pairs. First pair - our sat, second - fuel station (if present)
        'radius', # for hohmann problem (target orbit radius)
        'fuel2', # on fuel station
        'collected', # list of bools
        'moon', # moon also listed in 'objects' last
        )
    def haveMoon(self):
        return self.scenario >= 4001
    
    def __str__(self):
        return "{t=%s %s}"%(self.time,self.objects)
    
    @staticmethod
    def dists(s1,s2):
        return list(sqrt((x1-x2)**2+(y1-y2)**2) 
                   for (x1,y1),(x2,y2) in zip(s1.objects,s2.objects))

class VMInterface(object):
    def __init__(self, llvm):
        self.llvm = llvm
        self.currentStep = 0
        self.ax = 0.0
        self.ay = 0.0
        self.state = State()
        
    def clone(self):
        return deepcopy(self)
        

    def setAcceleration(self, ax, ay):
        self.ax, self.ay = ax, ay
        
    def run(self, steps = 1, ax = 0.0, ay = 0.0):
        """ low-level interface, won't play nice with executeSteps"""
        self.ax = ax
        self.ay = ay
        steps = self.llvm.run(steps, ax, ay)
        self.currentStep += steps
        self.updateState()
        return steps

    def executeSteps(self, steps, controls):
        if self.state.score != 0.0: return 0
        time = self.currentStep
        prevTime = time
        for time in xrange(time, time + steps):
            ctrl = controls.get(time)
            if ctrl is not None:
                # execute up to this point
                dt = time - prevTime
                if dt > 0:
                    executed = llvm.run(dt, self.ax, self.ay)
                    prevTime += executed
                    if executed != dt:
                        break
                self.ax, self.ay = ctrl
        executed = prevTime - self.currentStep
        dt = steps - executed
        if dt > 0:
            executed = llvm.run(dt, self.ax, self.ay)
            prevTime += executed
        executed = prevTime - self.currentStep
        self.currentStep = prevTime
        self.updateState()
        return executed
        
    def updateState(self):
        output = self.llvm.getoutput()
        self.state.time = self.currentStep
        self.state.score = output[0]
        self.state.fuel = output[1]
        self.state.objects = []
        
        x,y = (-output[2], -output[3])
        self.state.objects.append((x,y))
        self.state.r = sqrt(x**2 + y**2)
        if self.state.scenario >= 1001 and self.state.scenario <= 1004:
            self.state.radius = output[4]
        elif self.state.scenario >= 2001 and self.state.scenario <= 2004 or\
            self.state.scenario >= 3001 and self.state.scenario <= 3004:
            self.state.objects.append((x+output[4],y+output[5]))
        elif self.state.scenario >= 4001 and self.state.scenario <= 4004:
            # fuel station
            self.state.objects.append((x+output[4],y+output[5]))
            self.state.fuel2 = output[6]
            self.state.collected = []
            for i in range(12):
                self.state.objects.append((x+output[3*i+7],y+output[3*i+8]))
                self.state.collected.append(output[3*i+7] == 1.0)
            self.state.moon = (x+output[0x64],y+output[0x65])
            self.state.objects.append(self.state.moon)
        else:
            assert False,'unknown scenario'

    def getStats(self):
        assert False,"Stop using this deprecated shit! use 'state' instead"
        
    stats = property(getStats)

    def printState(self):
        print 'Score:',self.state.score
        print 'Fuel:',self.state.fuel
        print 'coords: ',self.state.objects[0]

def createScenario(fileName, scenario, vmconstructor):
    "returns vm"
    ctor = vmconstructor(fileName)
    vm = ctor.newvm(scenario)
    vmi = VMInterface(vm)
    vmi.run() # run one step
    assert vmi.state.time == 1
    return vmi

def getSolution(scenario,totalTime,controls):
    res = [struct.pack("<III",0xCAFEBABE,teamID,int(scenario))]
    
    res.append(struct.pack("<II",0,1))
    res.append(struct.pack("<Id",0x3E80,float(scenario)))

    px = 0.0
    py = 0.0
    for i in range(1,totalTime):
        x,y = controls.get(i,(0.0,0.0))
        k = 0
        if x != px:
            k += 1
        if y != py:
            k += 1
        if k > 0:
            res.append(struct.pack("<II",i,k))
            if x != px:
                res.append(struct.pack("<Id",2,float(x)))
            if y != py:
                res.append(struct.pack("<Id",3,float(y)))
        px,py = x,y
    res.append(struct.pack("<II",totalTime,0))
            
    return "".join(res)


        