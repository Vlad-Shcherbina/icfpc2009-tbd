from __future__ import with_statement

import sys
import os
import struct
import time
from operator import *
from math import *

from visualizer import *
from orbitvm import OrbitVM, DummyVM
from pyvmwrap import PyVM
from vm import VM
from solvers.hohmann import HohmannController
from solvers.meetgreet import MeetGreetController

if __name__ == '__main__':

    #vm = OrbitVM(OrbitVM.Hohmann, 1)
    #vm = OrbitVM(OrbitVM.Eccentric, 1)
    #vm = DummyVM(OrbitVM.ClearSkies, 1)
    
    config = 2

    if 0:
        with open("../../task/bin1.obf","rb") as fin:
            data = fin.read()
        vm = PyVM(data, OrbitVM.Hohmann, config)
        solver = HohmannController(vm.getVMImpl())
    elif 0:
        with open("../../task/bin2.obf","rb") as fin:
            data = fin.read()
        vm = PyVM(data, OrbitVM.MeetnGreet, config)
        solver = MeetGreetController(vm.getVMImpl())
    elif 0:
        with  open("../../task/bin3.obf","rb") as fin:
            data = fin.read()
        vm = PyVM(data, OrbitVM.Eccentric, config)
        solver = MeetGreetController(vm.getVMImpl())
    elif 1:
        with open("../../task/bin4.obf","rb") as fin:
            data = fin.read()
        vm = PyVM(data, OrbitVM.ClearSkies, config)
        solver = None
    
    
    kh = keyboardHandler
    #kh = None
    vis = Visualizer(vm, solver, scaler = 0, keyHandler = kh)

    vis.registerDrawer(StatsDrawer())
    
    vis.run()
