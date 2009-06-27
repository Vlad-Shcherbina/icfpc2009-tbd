from copy import deepcopy
from bisect import *

from vm import VM

class History(object):
    def __init__(self,vm,lookAhead=10000):
        assert vm.currentStep == 1
        vm = vm.clone()
        self.states = []
        self.times = []
        print 'calculating history ...',
        for i in range(lookAhead):
            self.states.append(deepcopy(vm.state))
            self.times.append(int(vm.state.time))
            vm.execute()
        print 'ok'
        
    def getStateByTime(self,time):
        assert isinstance(time,int)
        i = bisect_left(self.times,time)
        if i == len(self.times):
            return None
        if self.states[i].time != time:
            return None
        return self.states[i]
