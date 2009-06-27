import operator
import math

class asm(object):
    add = 'add'
    sub = 'sub'
    mul = 'mul'
    div = 'div'
    out = 'out'
    cmv = 'cmv'
    
    noop = 'noop'
    cmpz = 'cmpz'
    sqrt = 'sqrt'
    copy = 'copy'
    read = 'read'
    
    binaryopcodes = (add, sub, mul, div, out, cmv)
    unaryopcodes  = (noop, cmpz, sqrt, copy, read)
    cmpzops = ('<', '<=', '==', '>=', '>')
    cmpzfuncs = (operator.__lt__,
                 operator.__le__,
                 operator.__eq__,
                 operator.__ge__,
                 operator.__gt__)


class Operation(object):
    def __init__(self, addr, op):
        self.addr = addr
        opcode = op >> 28
        if opcode != 0:
            self.binary = True
            self.op = asm.binaryopcodes[opcode - 1]
            self.r1 = op >> 14 & 0x3FFF
            self.r2 = op & 0x3FFF
        else:
            self.binary = False
            opcode = op >> 24
            self.op = asm.unaryopcodes[opcode]
            if self.op == asm.cmpz:
                imm = op >> 21 & 0x7
                self.cmpzop = asm.cmpzops[imm]
                self.cmpzfunc = asm.cmpzfuncs[imm]
            self.r1 = op & 0x3FFF

    def __str__(self):
        if self.binary:
            s = "%s  %4d %4d" % (self.op, self.r1, self.r2)
        else:
            c = self.op
            if   c == asm.noop: s = "noop"
            elif c == asm.cmpz: s = "cmpz %2s   %4d" % (self.cmpzop, self.r1)
            else: s = "%s %4d" % (self.op, self.r1)
        return "%4d: %s" % (self.addr, s)
            
    def execute(self, memory, input, output, status):
        "memory is array, input/output are dictionaries, status is a list of 1 element"
        op = self.op
        if self.binary:
            a1, a2 = memory[self.r1], memory[self.r2]
            if   op == asm.add:
                memory[self.addr] = a1 + a2 
            elif op == asm.sub:
                memory[self.addr] = a1 - a2 
            elif op == asm.mul:
                memory[self.addr] = a1 * a2 
            elif op == asm.div:
                memory[self.addr] = a1 / a2 if a2 != 0.0 else 0.0  
            elif op == asm.out:
                output[self.r1] = a2 
            elif op == asm.cmv:
                memory[self.addr] = a1 if status[0] else a2
            else:
                raise Exception('WTF')
        else:  
            if   op == asm.noop:
                pass 
            elif op == asm.cmpz:
                status[0] = self.cmpzfunc(memory[self.r1], 0.0) 
            elif op == asm.sqrt:
                memory[self.addr] = math.sqrt(memory[self.r1]) 
            elif op == asm.copy:
                memory[self.addr] = memory[self.r1]  
            elif op == asm.read:
                memory[self.addr] = input[self.r1]
            else:
                raise Exception('WTF')
