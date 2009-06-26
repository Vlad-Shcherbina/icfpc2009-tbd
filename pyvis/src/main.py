import time

from visualizer import Visualizer
from orbitvm import OrbitVM


#vm = OrbitVM(OrbitVM.Hohmann, 1)
#vm = OrbitVM(OrbitVM.Eccentric, 1)
vm = OrbitVM(OrbitVM.ClearSkies, 1)

vis = Visualizer(vm)

vm.run()

vis.run()

