import sys
import os
import struct
import time
from operator import *
from math import *

from visualizer import Visualizer
from orbitvm import OrbitVM, DummyVM
from pyvmwrap import PyVM


if __name__ == '__main__':

    #vm = OrbitVM(OrbitVM.Hohmann, 1)
    #vm = OrbitVM(OrbitVM.Eccentric, 1)
    vm = DummyVM(OrbitVM.ClearSkies, 1)
    
    assert len(sys.argv) == 2
    fin = open(sys.argv[1],"rb")
    data = fin.read()
    #vm = PyVM(data, OrbitVM.Hohmann, 1)
    
    vis = Visualizer(vm)
    
    vm.run()
    
    vis.run()
    
