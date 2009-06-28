from __future__ import with_statement

import psyco
psyco.full()

from copy import copy,deepcopy

import struct
from operator import *
from math import *
from collections import defaultdict

__all__ = [
    "instrToStr",
    "teamID",
    "VM",
    "createScenario",
    "State",
]

teamID = 160

global Hohmann, MeetGreet, Eccentric, ClearSkies

Hohmann = range(1001,1005)
MeetGreet = range(2001,2005)
Eccentric = range(3001,3005)
ClearSkies = range(4001,4005)

EarthRadius = 6.357e6

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

class VM(object):
    def __init__(self,data):
        """
        Data is contents of vm binary
        """
        assert len(data)%12 == 0
        self.size = len(data)//12
        frames = [data[12*i:12*(i+1)] for i in range(self.size)]
        
        self.status = 0
        
        self.code = [0]*2**14
        self.mem = [0.0]*2**14
        self.prevInPort = defaultdict(float)
        self.inPort = defaultdict(float)
        self.outPort = defaultdict(float)
          
        for i in range(self.size):
            if i%2 == 0:
                value,instr = struct.unpack("<dI",frames[i])
            else:
                instr,value = struct.unpack("<Id",frames[i])
            self.code[i] = instr
            self.mem[i] = value

        self.currentStep = 0
        self.controlCommands = []
        
    def clone(self):
        return deepcopy(self)
        
    def writePort(self,addr,value):
        # Low-level method
        assert isinstance(value,float)
        self.inPort[addr] = value

    def setScenario(self,number):
        assert self.currentStep == 0
        self.scenario = int(number)
        self.writePort(0x3E80,float(number))
        self.state = State()
        self.state.scenario = float(number)
        
    def changeSpeed(self,dvx,dvy):
        assert self.currentStep > 0
        self.writePort(2,float(dvx))
        self.writePort(3,float(dvy))

    def saveControl(self,last=False):
        controlCommand = []
        for addr in sorted(set(self.inPort.keys())|set(self.prevInPort.keys())):
            if self.inPort[addr] != self.prevInPort[addr]:
                controlCommand.append(struct.pack("<Id",addr,self.inPort[addr]))
        if last or len(controlCommand) > 0:
            self.controlCommands.append(
                struct.pack("<II",
                            self.currentStep,
                            len(controlCommand)) +
                "".join(controlCommand) )
        self.prevInPort = copy(self.inPort)
    
    def execute(self,debug=False):
        """Perform one step of simulation"""
        self.saveControl()
        self.currentStep += 1
        i = 0
        if debug:
            print '           before'+' '*45+'after'
        for i in range(self.size):
            if debug:
                print "%20f"%self.mem[i],'  ',
            instr = self.code[i]
            dOp = instr>>28
                    
            if dOp != 0:
                r1 = (instr>>14)&0x3FFF
                r2 = instr&0x3FFF
                if dOp == 1:
                    self.mem[i] = self.mem[r1]+self.mem[r2]
                elif dOp == 2:
                    self.mem[i] = self.mem[r1]-self.mem[r2]
                elif dOp == 3:
                    self.mem[i] = self.mem[r1]*self.mem[r2]
                elif dOp == 4:
                    if self.mem[r2] == 0.0:
                        self.mem[i] = 0.0
                    else:
                        self.mem[i] = self.mem[r1]/self.mem[r2]
                elif dOp == 5:
                    self.outPort[r1] = self.mem[r2]
                elif dOp == 6:
                    if self.status == 1:
                        self.mem[i] = self.mem[r1]
                    else:
                        self.mem[i] = self.mem[r2]
                else:
                    assert False,'unknown D-op'
            else:
                sOp = instr>>24
                assert sOp <= 4
                r1 = instr&0x3FFF
                if sOp == 0:
                    self.mem[i] = self.mem[i]
                elif sOp == 1:
                    cmpOp = (instr>>21)&7
                    if [lt,le,eq,ge,gt][cmpOp](self.mem[r1],0.0):
                        self.status = 1
                    else:
                        self.status = 0
                elif sOp == 2:
                    self.mem[i] = sqrt(self.mem[r1])
                elif sOp == 3:
                    self.mem[i] = self.mem[r1]
                elif sOp == 4:
                    self.mem[i] = self.inPort[r1]
                else:
                    assert False,'unknown S-op'
            
            if debug:        
                print "%04X  %s % 0f"%(i,instrToStr(instr).ljust(30),self.mem[i]),
                print ';    status =',self.status
        self.changeSpeed(0,0)
        self.updateState()
        
    def updateState(self):
        self.state.time = self.currentStep
        self.state.score = self.outPort[0]
        self.state.fuel = self.outPort[1]
        self.state.objects = []
        x,y = (-self.outPort[2],-self.outPort[3])
        self.state.objects.append((x,y))
        self.state.r = sqrt(x**2 + y**2)
        if self.state.scenario >= 1001 and self.state.scenario <= 1004:
            self.state.radius = self.outPort[4]
        elif self.state.scenario >= 2001 and self.state.scenario <= 2004 or\
            self.state.scenario >= 3001 and self.state.scenario <= 3004:
            self.state.objects.append((x+self.outPort[4],y+self.outPort[5]))
        elif self.state.scenario >= 4001 and self.state.scenario <= 4004:
            # fuel station
            self.state.objects.append((x+self.outPort[4],y+self.outPort[5]))
            self.state.fuel2 = self.outPort[6]
            self.state.collected = []
            for i in range(12):
                self.state.objects.append((x+self.outPort[3*i+7],y+self.outPort[3*i+8]))
                self.state.collected.append(self.outPort[3*i+7] == 1.0)
            self.state.moon = (x+self.outPort[0x64],y+self.outPort[0x65])
            self.state.objects.append(self.state.moon)
        else:
            assert False,'unknown scenario'

    def getStats(self):
        assert False,"Stop using this deprecated shit! use 'state' instead"
    stats = property(getStats)

    def printStats(self):
        print 'Score:',self.state.score
        print 'Fuel:',self.state.fuel
        print 'coords: ',self.state.objects[0]
        
    def memDump(self):
        for i in range(self.size):
            print "%04X %f"%(i,self.mem[i])
            
    def getSolution(self):
        if self.state.score <= 0.0:
            print "Warning: (getSolution)"\
                "score is nonpositive!!!!!!!!!!",self.state.score
        self.saveControl(last=True)
        return struct.pack("<III",0xCAFEBABE,teamID,int(self.state.scenario))+\
            "".join(self.controlCommands)

def createScenario(fileName,scenario):
    "returns vm"
    with open(fileName,"rb") as fin:
        data = fin.read()
    vm = VM(data)
    
    vm.setScenario(scenario)
    vm.execute()
    
    return vm

def instrToStr(instr):
    dOp = instr>>28
    if dOp != 0:
        r1 = (instr>>14)&0x3FFF
        r2 = instr&0x3FFF
        fmt = {
            1:"add mem[%(r1)04X],mem[%(r2)04X]",
            2:"sub mem[%(r1)04X],mem[%(r2)04X]",
            3:"mul mem[%(r1)04X],mem[%(r2)04X]",
            4:"div mem[%(r1)04X],mem[%(r2)04X]",
            5:"write outPort[%(r1)04X],mem[%(r2)04X]",
            6:"phi mem[%(r1)04X],mem[%(r2)04X]",
            }[dOp]
    else:
        sOp = instr>>24
        r1 = instr&0x3FFF
        cmpOp = (instr>>20)&15
        cmpStr = ['<','<=','=','>=','>'][cmpOp]
        fmt = {
            0:'noop',
            1:'cmp mem[%(r1)04X] %(cmpStr)s 0.0',
            2:'sqrt mem[%(r1)04X]',
            3:'copy mem[%(r1)04X]',
            4:'input inPort[%(r1)04X]',
            }[sOp]

    return fmt%locals()
        