from __future__ import with_statement

import sys
import os
import struct
import time
from operator import *
from math import *

from visualizer import *

from vm import VM
from vm import Hohmann, MeetGreet, Eccentric, ClearSkies

from solvers.hohmann import HohmannController
from solvers.meetgreet import MeetGreetController

if __name__ == '__main__':

    #vm = OrbitVM(OrbitVM.Hohmann, 1)
    #vm = OrbitVM(OrbitVM.Eccentric, 1)
    #vm = DummyVM(OrbitVM.ClearSkies, 1)
    
    config = 2

    if 1:
        with open("../../task/bin1.obf","rb") as fin:
            data = fin.read()
        vm = VM(data)
        vm.setScenario(Hohmann[config-1])
        solver = HohmannController(vm)
    elif 0:
        with open("../../task/bin2.obf","rb") as fin:
            data = fin.read()
        vm = VM(data)
        vm.setScenario(MeetGreet[config-1])
        solver = MeetGreetController(vm)
    elif 0:
        with  open("../../task/bin3.obf","rb") as fin:
            data = fin.read()
        vm = VM(data)
        vm.setScenario(Eccentric[config-1])
        solver = MeetGreetController(vm)
    elif 1:
        with open("../../task/bin4.obf","rb") as fin:
            data = fin.read()
        vm = VM(data)
        vm.setScenario(ClearSkies[config-1])
        solver = None
    
    
    kh = keyboardHandler
    #kh = None
    vis = Visualizer(vm, solver, scaler = 0, keyHandler = kh)

    vis.registerDrawer(StatsDrawer())
    vis.registerDrawer(RadiusDrawer())
    
    vis.run()
