from struct import unpack_from
import itertools
from instructions import asm, Operation

MAX_OUT_PORTS = 6 + 12 * 3

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

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

def decode_ops(ops, data):
    return [OperationEx(addr, op, datum) for addr, (op, datum) in enumerate(zip(ops, data))] 

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

class kinds():
    """Used by OperationEx"""
    ignore = 'ignore'
    constant = 'constant'
    variable = 'variable'
    output = 'output'
    input = 'input'

class OperationEx(Operation):
        
    def __init__(self, *args, **kwargs):
        Operation.__init__(self, *args, **kwargs)
        self.uses = []
        self.usedby = []
        self.reachable = False
    
    def updateLink(self, op):
        self.uses.append(op)
        op.usedby.append(self)
        
    def updateLinks(self, ops):
        op = self.op
        if   op in (asm.add, asm.sub, asm.div, asm.mul):
            self.updateLink(ops[self.r1])
            self.updateLink(ops[self.r2])
        elif op == asm.out:
            self.updateLink(ops[self.r2])
        elif op == asm.cmv:
            self.updateLink(ops[self.r1])
            self.updateLink(ops[self.r2])
            for cond in ops[self.addr - 1 :: -1]:
                if cond.op == asm.cmpz:
                    self.updateLink(cond)
                    break
            else:
                assert False, 'cmv without cmpz (it is actually allowed, by the way)'
        elif op in (asm.noop, asm.read):
            pass
        elif op in (asm.cmpz, asm.copy, asm.sqrt):
            self.updateLink(ops[self.r1])
        else:
            assert False, 'WTF?!'
    
    def __str__(self):
        s = Operation.__str__(self)
        def opaddrs(lst):
            return "[" + ", ".join(str(op.addr) for op in lst) + "]" 
        s = s.ljust(25) + (" uses: " + opaddrs(self.uses)).ljust(30)
        s += " used by " + opaddrs(self.usedby)
        # s += " kind: " + self.kind
        if not self.reachable: s = '*' + s
        else: s = ' ' + s
        return s
    
    def mark_reachable(self, reachable = False):
        if not self.reachable:
            if self.op == asm.out: reachable = True
            if reachable:
                self.reachable = True
                for o in self.uses:
                    o.mark_reachable(True)
    
    def determine_kind(self):
        if self.op == asm.out:
            assert len(self.usedby) == 0
            self.read_kind = kinds.constant
            self.write_kind = kinds.output
        elif len(self.usedby) == 0:
            self.write_kind = kinds.ignore
        elif self.op == asm.read:
            assert len(self.uses) == 0
            self.read_kind = kinds.input
            self.write_kind = kinds.variable
            
            if self.r1 not in (1, 2, 16000):
                print 'Read out of range:', self
                self.kind = kinds.constant
       #         self.
        elif len(self.uses) == len(self.usedby) == 0:
            self.kind = kinds.ignore
        else:
            self.kind = kinds.variable
             
        


def analyzeops(ops):
    for op in ops: op.updateLinks(ops)
    for op in ops: op.mark_reachable()
    reachable = []
    for op in ops:
        if op.reachable: reachable.append(op)
        else: print 'Unreachable:', op 
    
    for op in ops:
        print op
    return ops

def process_file(n):
    filename = '../../task/bin%d.obf' % n
    print 'Processing', filename
    src = open(filename, 'rb').read()
    code, data = decode_src(src)
    ops = decode_ops(code, data)
    analyzeops(ops)
    
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
