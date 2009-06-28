import struct
import itertools
from instructions import asm, Operation

MAX_OUT_PORTS = 0x70

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

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
            for cond in ops[self.addr - 1 :: -1]:
                if cond.op == asm.cmpz:
                    self.updateLink(cond)
                    break
            else:
                assert False, 'cmv without cmpz (it is actually allowed, by the way)'
            self.updateLink(ops[self.r1])
            self.updateLink(ops[self.r2])
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
        return s
    
    def mark_reachable(self, reachable = False):
        if not self.reachable:
            if self.op == asm.out: reachable = True
            if reachable:
                self.reachable = True
                for o in self.uses:
                    o.mark_reachable(True)
    
    def determine_type(self):
        self.temporary = False
        
        self.variable = False
        self.local_variable = False
        self.persistent_variable = False
        
        self.constant = False
        self.inline_constant = False
        self.declared_constant = False
        
        self.statement = False
        
        if self.op in (asm.out, asm.noop, asm.cmpz): 
            # cmpz's value is resolved using getcmpzvalue
            self.constant = True
            repr = '%0.0f' % self.data
            if float(repr) == self.data and len(repr) < 19:
                self.inline_constant = True
            else:
                self.declared_constant = True
            
        if len(self.usedby) == 1 and self.op != asm.read:
            # except for divisor
            user = self.usedby[0]
            if user.addr >= self.addr and (user.op != asm.div or user.r2 != self.addr): 
                self.temporary = True
        
        if not self.temporary and not self.constant:
            self.variable = True
            if self.addr < min(op.addr for op in self.usedby):
                self.local_variable = True
            else:
                self.persistent_variable = True
            
        if self.variable or self.op == asm.out:
            self.statement = True
        
    
    simple_reprs = {
            asm.add : '({0} + {1})',
            asm.sub : '({0} - {1})',
            asm.mul : '({0} * {1})',
            # asm.div : 'div({0} / {1})',
            #     using an inline function,
            #     but with a special case when {1} is constant (for readability).
            # asm.out - constant
            # asm.cmv : '({0} ? {1} : {2})',
            #     special case - comparison not via getvalue. 
            
            # asm.noop - constant
            # asm.cmpz - constant
            asm.sqrt : 'sqrt({0})',
            asm.copy : '{0}',
            # asm.read - special case
        }
    
    def getexpression(self):
        args = (arg.getvalue() for arg in self.uses) # MUST BE LAZY!
        simple_repr = self.simple_reprs.get(self.op)
        if simple_repr:
            return simple_repr.format(*args)
        if self.op == asm.div:
            if self.uses[1].constant: 
                if self.uses[1].data == 0.0: return "0.0" 
                else:
                    return '({0} / {1})'.format(*args)
            else: return 'div({0}, {1})'.format(*args)
        if self.op == asm.cmv:
            return '({0} ? {1} : {2})'.format(self.uses[0].getcmpzvalue(),
                self.uses[1].getvalue(), self.uses[2].getvalue())
        if self.op == asm.read:
            if self.r1 in (2, 3, 16000):
                return 'i%d' % self.r1
            else:
                print 'Warning, reading from unassigned input register', self
                return '0.0'
        raise "WTF!"
    
    def getvarname(self):
        assert self.variable
        if self.local_variable:
            return "lv" + str(self.addr)
        else:
            return "pv" + str(self.addr)
        
    def getvaraccess(self):
        if self.local_variable: return self.getvarname()
        else: return 'memory[{0}]'.format(self.getvarname())
        

    def getconstname(self):
        assert self.declared_constant
        return "c" + str(self.addr)
    
    def getvalue(self):
        if self.variable: return self.getvaraccess()
        if self.inline_constant: return repr(self.data) 
        if self.declared_constant: return self.getconstname() 
        if self.temporary: return self.getexpression() 
        raise "WTF!"
                
    def getcmpzvalue(self):
        assert self.op == asm.cmpz
        return '({0} {1} 0.0)'.format(self.uses[0].getvalue(), self.cmpzop)
    
        
    def getconstdeclaration(self):
        assert self.declared_constant
        iname = 'long_' + str(self.addr)
        ivalue = "".join('%02X' % ord(c) for c in reversed(struct.pack('d', self.data)))  
        s1 = 'const unsigned long long {0} = 0x{1}L;'.format(iname, ivalue)
        s2 = 'const double {0} = *(double*)&{1};'.format(
            self.getconstname(), iname)
#        s1 = ''
#        s2 = 'const double {0} = {1};'.format(self.getconstname(), repr(self.data))
        s2 = s2.ljust(45)
        s2 += '// ' + str(self.data)
        return s1 + '\n' + s2 + '\n'
            
        
    def getstatement(self):
        def strip_parens(s):
            if s.startswith('(') and s.endswith(')'):
                return s[1:-1]
            return s
        
        assert self.statement
        if self.op == asm.out:
            return 'output[{0}] = {1};'.format(self.r1, strip_parens(self.uses[0].getvalue()))
        else:
            return '{0} = {1};'.format(self.getvaraccess(), strip_parens(self.getexpression()))
    
    def getindexdeclaration(self, index):
        assert self.persistent_variable
        return 'const int {0} = {1};'.format(self.getvarname(), index)
    def getlocalvardeclaration(self):
        assert self.local_variable
        return 'double {0};'.format(self.getvarname())
        
        


def create_compilation_items(ops):
    for op in ops: op.updateLinks(ops)
    for op in ops: op.mark_reachable()
    reachable = []
    for op in ops:
        if op.reachable: reachable.append(op)
        else: print 'Unreachable:', op 
    ops = reachable
    for op in ops: op.determine_type()
    
    declared_constants = [op.getconstdeclaration() for op in ops if op.declared_constant]
    var_indices = [op.getindexdeclaration(i) for i, op in enumerate(
                    op for op in ops if op.persistent_variable)]
    var_declarations = [op.getlocalvardeclaration() for op in ops if op.local_variable]
    statements = [op.getstatement() for op in ops if op.statement]
    data = [op.data for op in ops if op.persistent_variable]
    datamap = [op.addr for op in ops if op.persistent_variable]
    
    return ('\n'.join(declared_constants + var_indices + var_declarations) + '\n', 
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
        ops.append(OperationEx(i, instr, value))
    return ops
    

vm_description = namedtuple('vm_description', 
    'declarations statements memorysize outputsize memory memorymap')

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
    print data
    vm = vm_description(declarations, statements, len(data), MAX_OUT_PORTS, 
                        tuple(data), tuple(datamap))
    
#    memory = list(data)
#    input = {2:0.0, 3:0.0, 16000:1001.0}
#    output = {}
#    status = [0]
#    for op in ops:
#        op.execute(memory, input, output, status)
#    print memory
#    print output
  
    return vm

