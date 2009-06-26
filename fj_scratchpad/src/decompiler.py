from struct import unpack_from
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
                             
def decode_src(buf):
    l = len(buf)
    assert l % 12 == 0, "Length is not multiple of 12"
    code = []
    data = []
    
    for i in range(l // 12):
        if i % 2 == 0:
            value, instr = unpack_from("<di", buf, i * 12)
        else:
            instr, value = unpack_from("<id", buf, i * 12)
        code.append(instr)
        data.append(value)
    return code, data


class BinaryOp(object):
    def __init__(self, addr, op):
        self.addr = addr
        self.opcode = op >> 28
        self.op = asm.binaryopcodes[self.opcode - 1]
        self.r1 = op >> 14 & 0x3FFF
        self.r2 = op & 0x3FFF
        
    def __str__(self):
        return "%4d: %s  %4d %4d" % (self.addr, self.op, self.r1, self.r2)
    
    def execute(self, memory, input, output, status):
        "memory is array, input/output are dictionaries, status is list of 1 element"
        op = self.op
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
        

class UnaryOp(object):
    def __init__(self, addr, op):
        self.addr = addr
        assert op >> 28 == 0
        self.opcode = op >> 24
        self.op = asm.unaryopcodes[self.opcode]
        self.imm = op >> 21 & 0x7
        if self.op == asm.cmpz:
            self.cmpzop = asm.cmpzops[self.imm]
            self.cmpzfunc = asm.cmpzfuncs[self.imm]
        self.r1 = op & 0x3FFF
        
    def __str__(self):
        c = self.op
        if   c == asm.noop: return "noop"
        elif c == asm.cmpz: return "cmpz %2s   %4d" % (self.cmpzop, self.r1)
        else: return "%4d: %s %4d" % (self.addr, self.op, self.r1)

    def execute(self, memory, input, output, status):
        "memory is array, input/output are dictionaries, status is list of 1 element"
        op = self.op
        noop = 'noop'
        cmpz = 'cmpz'
        sqrt = 'sqrt'
        copy = 'copy'
        read = 'read'
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



def decode_op(addr, op):
    return UnaryOp(addr, op) if op >> 28 == 0 else BinaryOp(addr, op)

def decode_ops(ops):
    return [decode_op(addr, op) for addr, op in enumerate(ops)] 


def execute_ops(ops, data):
    memory = list(data)
    input = {2 : 0.0, 3 : 0.0, 0x3E80 : 1001.0 }
    output = {}
    status = [0]
    for op in ops: 
        try: 
            op.execute(memory, input, output, status)
        except:
            print op
            raise
    #open('memdump.txt', 'w').writelines('%04X %f\n' % (i, f) for i, f in enumerate(memory))
    return output

def process_file(n):
    src = open('../../task/bin%d.obf' % n, 'rb').read()
    code, data = decode_src(src)
    ops = decode_ops(code)
    print execute_ops(ops, data)
    
#    outfile = open('disassembly%d' % n, 'w')    
#    
#    outfile.write('Data:\n')
#    for i, d in enumerate(data):
#        outfile.write('%4d: %s\n' % (i, '--' if d == 0 else '%0.5f' % d))
#    
#    outfile.write('\n\nCode:\n')
#    for i, d in enumerate(ops):
#        outfile.write('%4d: %s\n' % (i, str(d)))
#    
#    outfile.close()

if __name__ == '__main__':
    for i in range(1):
        process_file(i + 1)
