from struct import unpack_from

class asm(object):
    add = 'add'
    sub = 'sub'
    mul = 'mul'
    div = 'div'
    out = 'out'
    mov = 'mov'
    
    noop = 'noop'
    cmpz = 'cmpz'
    sqrt = 'sqrt'
    copy = 'copy'
    read = 'read'
    
    binaryopcodes = (add, sub, mul, div, out, mov)
    unaryopcodes  = (noop, cmpz, sqrt, copy, read)
    cmpzops = ('<', '<=', '==', '>=', '>') 
                             
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
    def __init__(self, op):
        self.opcode = op >> 28
        self.op = asm.binaryopcodes[self.opcode - 1]
        self.r1 = op >> 14 & 0x3FFF
        self.r2 = op & 0x3FFF
        
    def __str__(self):
        return "%s  %4d %4d" % (self.op, self.r1, self.r2) 
        
class UnaryOp(object):
    def __init__(self, op):
        assert op >> 28 == 0
        self.opcode = op >> 24
        self.op = asm.unaryopcodes[self.opcode]
        self.imm = op >> 20 & 0xF
        if self.op == asm.cmpz:
            self.cmpzop = asm.cmpzops[self.imm]
        self.r1 = op & 0x3FFF
        
    def __str__(self):
        c = self.op
        if   c == asm.noop: return "noop"
        elif c == asm.cmpz: return "cmpz %2s   %4d" % (self.cmpzop, self.r1)
        else: return "%s %4d" % (self.op, self.r1)


def decode_op(op):
    return UnaryOp(op) if op >> 28 == 0 else BinaryOp(op) 

def process_file(n):
    src = open('../../task/bin%d.obf' % n, 'rb').read()
    code, data = decode_src(src)
    outfile = open('disassembly%d' % n, 'w')    
    
    outfile.write('Data:\n')
    for i, d, in enumerate(data):
        outfile.write('%4d: %s\n' % (i, '--' if d == 0 else '%0.5f' % d))
    
    outfile.write('\n\nCode:\n')
    for i, d, in enumerate(code):
        outfile.write('%4d: %s\n' % (i, str(decode_op(d))))
    
    outfile.close()

if __name__ == '__main__':
    for i in range(3):
        process_file(i + 1)
