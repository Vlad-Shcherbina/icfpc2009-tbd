import sys
import os
import struct
from operator import *
from math import *

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


class VM(object):
    def __init__(self,data):
        assert len(data)%12 == 0
        self.size = len(data)//12
        frames = [data[12*i:12*(i+1)] for i in range(self.size)]
        
        self.status = 0
        
        self.code = [0]*2**14
        self.mem = [0.0]*2**14
        self.inPort = [0.0]*2**14
        self.outPort = [0.0]*2**14
          
        for i in range(self.size):
            if i%2 == 0:
                value,instr = struct.unpack("<dI",frames[i])
            else:
                instr,value = struct.unpack("<Id",frames[i])
            self.code[i] = instr
            self.mem[i] = value

        print '%x'%self.code[6]
#        for i in range(self.size):
#            print self.code[i],self.mem[i]

    def execute(self,debug=False):
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
    def printStats(self):
        print 'Score:',self.outPort[0]
        print 'Fuel:',self.outPort[1]
        print 'sx ',self.outPort[2]
        print 'sy ',self.outPort[3]
        
    def memDump(self):
        for i in range(self.size):
            print "%04X %f"%(i,self.mem[i])
                    

if __name__ == '__main__':
    assert len(sys.argv) == 2
    print os.getcwd()
#    with open(sys.argv[1],"rb") as fin:
 #       data = fin.read()
        
    vm = VM(data)
    vm.inPort[0x3E80] = 1001.0
    while vm.outPort[0] == 0.0:
        vm.printStats()
        print 'step'
        vm.execute()
        vm.memDump()
        break
        vm.printStats()
    
    
    
    print 'ok'