import sys
import os
import struct
import time
from operator import *
from math import *

from visualizer import Visualizer
from orbitvm import OrbitVM, DummyVM
from pyvmwrap import PyVM

from solvers.hohmann_transfer import transfer


if __name__ == '__main__':

    #vm = OrbitVM(OrbitVM.Hohmann, 1)
    #vm = OrbitVM(OrbitVM.Eccentric, 1)
    #vm = DummyVM(OrbitVM.ClearSkies, 1)
    
    config = 1

    if 1:
        fin = open("../../task/bin1.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.Hohmann, config)
        solver = transfer(vm.getVMImpl())
    elif 1:
        fin = open("../../task/bin2.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.MeetnGreet, config)
        solver = transfer(vm.getVMImpl())
    elif 0:
        fin = open("../../task/bin3.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.Eccentric, config)
        solver = None
    elif 0:
        fin = open("../../task/bin4.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.ClearSkies, config)
        solver = None
    
    vis = Visualizer(vm, solver)
    
    vis.run()
