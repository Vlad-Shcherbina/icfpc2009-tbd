from __future__ import with_statement

import sys
import os
import struct
import time
from operator import *
from math import *

from visualizer import *

import vm
from visualizer import Hohmann, MeetGreet, Eccentric, ClearSkies

from solvers.hohmann import HohmannController
from solvers.meetgreet import MeetGreetController, MeetGreetLasyController

if __name__ == '__main__':

    #vm = OrbitVM(OrbitVM.Hohmann, 1)
    #vm = OrbitVM(OrbitVM.Eccentric, 1)
    #vm = DummyVM(OrbitVM.ClearSkies, 1)
    
    config = 4

    if 0:
        vm = vm.createScenario("../../task/bin1.obf", Hohmann[config-1])
        solver = HohmannController(vm)
    elif 1:
        vm = vm.createScenario("../../task/bin2.obf", MeetGreet[config-1])
        solver = MeetGreetController(vm)
        #solver = MeetGreetLasyController(vm)
    elif 1:
        vm = vm.createScenario("../../task/bin3.obf", Eccentric[config-1])
        solver = MeetGreetController(vm)
    elif 1:
        vm = vm.createScenario("../../task/bin4.obf", ClearSkies[config-1])
        solver = None
    
    kh = keyboardHandler
    #kh = None
    vis = Visualizer(vm, solver, scaler = 0, keyHandler = kh)

    vis.registerDrawer(StatsDrawer())
    vis.registerDrawer(RadiusDrawer())
    #vis.registerDrawer(PredictDrawer())
    vis.registerDrawer(solver)
    
    vis.run()
