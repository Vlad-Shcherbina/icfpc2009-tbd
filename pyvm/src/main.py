import sys
import os
import struct

class VM(object):
    def __init__(self,data):
        assert len(data)%12 == 0
        size = len(data)//12
        frames = [data[12*i:12*(i+1)] for i in range(size)]
        self.code = [0]*2**14
        self.memory = [0.0]*2**14
          
        for i in range(size):
            if i%2 == 0:
                value,instr = struct.unpack("<di",frames[i])
            else:
                instr,value = struct.unpack("<id",frames[i])
            self.code[i] = instr
            self.memory[i] = value

        for i in range(size):
            print self.code[i],self.memory[i]
#        print self.instructions
#        print self.memory

if __name__ == '__main__':
    assert len(sys.argv) == 2
    print os.getcwd()
    with open(sys.argv[1],"rb") as fin:
        data = fin.read()
        
    vm = VM(data)