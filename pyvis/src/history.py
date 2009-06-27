from copy import deepcopy
from vm import VM

class History(object):
    def __init__(self,vm,lookAhead=10000):
        assert vm.currentStep == 1
        vm = vm.clone()
        self.states = []
        print 'calculation history ...',
        for i in range(lookAhead):
            self.states.append(deepcopy(vm.state))
            vm.execute()
        print 'ok'
