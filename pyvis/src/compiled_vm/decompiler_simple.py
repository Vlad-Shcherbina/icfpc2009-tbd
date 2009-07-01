import struct
import itertools
from collections import namedtuple
from instructions import asm, Operation

MAX_OUT_PORTS = 0x70

def create_compilation_items(ops):
    data = [op.data for op in ops]
    datamap = [op.addr for op in ops]

    simple_reprs = {
            asm.add : 'memory[{0}] + memory[{1}]',
            asm.sub : 'memory[{0}] - memory[{1}]',
            asm.mul : 'memory[{0}] * memory[{1}]',
            asm.div : 'div(memory[{0}], memory[{1}])',
            # asm.out  
            asm.cmv : 'status ? memory[{0}] : memory[{1}]',
            # asm.noop 
            # asm.cmpz 
            # asm.sqrt 
            # asm.copy 
            # asm.read
        }
    
    def getstatement(op):
        type = op.op
        sr = simple_reprs.get(type)
        if sr:
            return 'memory[{0}] = {1};'.format(op.addr, sr.format(op.r1, op.r2))
        elif type == asm.out:
            return 'output[{0}] = memory[{1}];'.format(op.r1, op.r2)
        elif type == asm.noop:
            return '// noop'
        elif type == asm.cmpz:
            return 'status = memory[{0}] {1} 0.0;'.format(op.r1, op.cmpzop)
        elif type == asm.sqrt:
            return 'memory[{0}] = sqrt(memory[{1}]);'.format(op.addr, op.r1)
        elif type == asm.copy:
            return 'memory[{0}] = memory[{1}];'.format(op.addr, op.r1)
        elif type == asm.read:
            if op.r1 in (2, 3, 16000):
                src = 'i%d' % op.r1
            else:
                print 'Warning, reading from unassigned input register', op
                src = '0.0'
            return 'memory[{0}] = {1};'.format(op.addr, src)
        else:
            raise 'WTF'
        
    statements = [getstatement(op) for op in ops]
    
    return ('int status = 0;\n\n', 
            '\n'.join(statements) + '\n',
            data,
            datamap) 

def decode_src(buf):
    l = len(buf)
    assert l % 12 == 0, "Length is not multiple of 12"
    ops = []
    
    for i in range(l // 12):
        if i % 2 == 0:
            value, instr = struct.unpack_from("<di", buf, i * 12)
        else:
            instr, value = struct.unpack_from("<id", buf, i * 12)
        ops.append(Operation(i, instr, value))
    return ops
    

class vm_description(object):
    def __init__(self, declarations, statements, memorysize, outputsize, memory, memorymap):
        self.declarations = declarations
        self.statements = statements
        self.memorysize = memorysize
        self.outputsize = outputsize
        self.memory = memory
        self.memorymap = memorymap

 
def process_file(filename):
    src = open(filename, 'rb').read()
    ops = decode_src(src)
    declarations, statements, data, datamap = create_compilation_items(ops)
    vm = vm_description(declarations, statements, len(data), MAX_OUT_PORTS, 
                        tuple(data), tuple(datamap))
    return vm

