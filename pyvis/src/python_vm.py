from copy import copy, deepcopy
from collections import defaultdict
import time
import struct
from operator import lt,le,eq,ge,gt
from math import sqrt

debug = 0

class PythonVM(object):
    def __init__(self, parent, scenario, state = None):
        self.scenario = float(scenario)
        self.parent = parent
        self.code = parent.code
        if state is None:
            self.reset()
        else:
            self.mem = deepcopy(state[0])
            self.status = deepcopy(state[1])
            self.output = deepcopy(state[2])
        
    
    def run(self, steps = 1, ax = 0.0, ay = 0.0):
        ax = float(ax)
        ay = float(ay)
        for step in range(steps):
            if self.output[0] != 0.0: return step
            
            if debug:
                print '           before'+' '*45+'after'
            for i in range(len(self.code)):
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
                        self.output[r1] = self.mem[r2]
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
                        if r1 == 2:
                            r = ax
                        elif r1 == 3:
                            r = ay
                        elif r1 == 16000:
                            r = self.scenario
                        else:
                            print "Warning: reading from undefined port", r1
                            r = 0.0
                        self.mem[i] = r
                    else:
                        assert False,'unknown S-op'
                
                if debug:        
                    print "%04X  %s % 0f"%(i,instrToStr(instr).ljust(30),self.mem[i]),
                    print ';    status =',self.status
        return steps

    def getoutput(self):
        return self.output
    
    def clearoutput(self):
        self.output.clear()
    
    def reset(self):
        self.status = 0
        self.mem = list(self.parent.mem)
        self.output = defaultdict(float)
    
    def __copy__(self):
        return self.clone()
    
    def __deepcopy__(self, d):
        return self.clone()
    
    def clone(self):
        state = (self.mem, self.status, self.output)
        return PythonVM(self.parent, self.scenario, state)
         


class PythonVMConstructor(object):
    def __init__(self, filename):
        data = open(filename, 'rb').read()
        assert len(data)%12 == 0
        size = len(data)//12
        frames = [data[12*i:12*(i+1)] for i in range(size)]
        
        self.code = [] 
        self.mem = []

        for i in range(size):
            if i%2 == 0:
                value,instr = struct.unpack("<dI",frames[i])
            else:
                instr,value = struct.unpack("<Id",frames[i])
            self.code.append(instr)
            self.mem.append(value)
        
        self.code = tuple(self.code)
        self.mem = tuple(self.mem)
        
    def newvm(self, scenario):
        return PythonVM(self, scenario)

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

if __name__ == '__main__':
    constructor = PythonVMConstructor('../../task/bin4.obf')
    vm = constructor.newvm(4001.0)
    
    clock = time.clock()   
    print vm.run(10000, 0, 0)
    print time.clock() - clock
    print vm.getoutput()
    
    
    