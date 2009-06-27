from math import sqrt, pi
from orbital import mu, getSpin

dV1 = lambda r1, r2: sqrt(mu/r1) * (sqrt(2*r2/(r1+r2)) - 1)
dV2 = lambda r1, r2: sqrt(mu/r2) * (1 - sqrt(2*r1/(r1+r2)))



class TransferController:
    def __init__(self, vm):
        self.vm = vm
        vm.execute()
        r1 = sqrt(vm.stats.sx**2 + vm.stats.sy**2)
        r2 = vm.outPort[4]
        self.trans = transfer(r1, r2)
        
    def step(self):
        self.trans.step(self.vm)



class transfer:
    def __init__(self, r1, r2, spin=0):
        self.r1 = r1
        self.r2 = r2
        self.direction = 1 if self.r2 > self.r1 else -1
        self.spin = spin
        assert spin in (-1,0,1)
        if spin == 0:
            self.state = 0
        else:
            self.state = 1

    def step(self, vm):
        sx, sy = vm.stats.sx, vm.stats.sy
        r = sqrt(sx**2 + sy**2)

        if self.state == 0:
            # sample the trajectory to determine which way we are going

            self.sxInit, self.syInit = sx, sy
            self.state = 1
            return 0

        elif self.state == 1:
            # make the first pulse

            if self.spin == 0:
                self.spin = getSpin(self.sxInit, self.syInit, sx, sy)

            dV = self.spin * self.direction * dV1(self.r1, self.r2)
            dVx =  sy * dV / self.r1
            dVy = -sx * dV / self.r1
            vm.changeSpeed(dVx, dVy)

            self.lastR = r
            self.state = 2
            return 0

        elif self.state == 2:
            # wait for the apogee, then make the second pulse

            if self.r1 < self.lastR < r or self.r1 > self.lastR > r:
                self.lastR = r
                return 0
            else: # if we are going back, we are past the peak
                dV = self.spin * self.direction * dV2(self.r1, self.r2)
                dVx =  sy * dV / r
                dVy = -sx * dV / r
                vm.changeSpeed(dVx, dVy)
                self.state = 3
                return self.spin
            
        elif self.state == 3:
            pass
        
def predictPosition(sx, sy, r2):
    """ Predict the coordinates after a Hohmann transfer from the current orbit to r2. """
    
    r1 = sqrt(sx**2 + sy**2)
    return (-r2 * sx/r1, -r2 * sy/r1)

def timeRequired(r1, r2):
    return pi * sqrt((r1+r2)**3/(8*mu))
    
    
    
