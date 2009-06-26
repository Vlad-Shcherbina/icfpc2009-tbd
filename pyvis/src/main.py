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
    #vm = DummyVM(OrbitVM.ClearSkies, 1)
    
    config = 2

    if 0:
        fin = open("../../task/bin1.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.Hohmann, config)
    elif 0:
        fin = open("../../task/bin2.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.MeetnGreet, config)
    elif 1:
        fin = open("../../task/bin3.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.Eccentric, config)
    elif 0:
        fin = open("../../task/bin4.obf","rb")
        data = fin.read()
        vm = PyVM(data, OrbitVM.ClearSkies, config)
    
    vis = Visualizer(vm)
    
    vis.run()
