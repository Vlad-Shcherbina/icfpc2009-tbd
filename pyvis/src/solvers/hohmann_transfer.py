from math import sqrt, pi
from orbital import mu, getSpin

dV1 = lambda r1, r2: sqrt(mu/r1) * (sqrt(2*r2/(r1+r2)) - 1)
dV2 = lambda r1, r2: sqrt(mu/r2) * (1 - sqrt(2*r1/(r1+r2)))

class transfer:
    def __init__(self, r1, r2, spin=0):
        self.r1 = r1
        self.r2 = r2
        self.spin = spin
        assert spin in (-1,0,1)
        if spin == 0:
            self.state = 0
        else:
            self.state = 1

    def step(self, vm):
        sx, sy = vm.stats.sx, vm.stats.sy
        r = sqrt(sx**2 + sy**2)

        assert (0 <= self.state <= 3)

        if self.state == 0:
            # sample the trajectory to determine which way we are going

            self.sxInit, self.syInit = sx, sy
            self.state = 1
            return 0

        elif self.state == 1:
            # make the first pulse

            if self.spin == 0:
                self.spin = getSpin(self.sxInit, self.syInit, sx, sy)

            dV = self.spin * dV1(self.r1, self.r2)
            dVx =  sy * dV / self.r1
            dVy = -sx * dV / self.r1
            vm.changeSpeed(dVx, dVy)

            #self.lastR = r
            self.timeLeft = int(round(timeRequired(self.r1, self.r2)))
            self.state = 2
            return 0

        elif self.state == 2:
            # wait for the transfer to be over, then make the second pulse

            self.timeLeft -= 1
            
            if self.timeLeft == 0:
                dV = self.spin * dV2(self.r1, self.r2)
                dVx =  sy * dV / r
                dVy = -sx * dV / r
                vm.changeSpeed(dVx, dVy)
                self.state = 3
                return self.spin
            else:
                return 0
            
        elif self.state == 3:
            return self.spin
    
    def performTransfer(self, vm):
        completed = 0
        while vm.outPort[0] == 0.0 and completed == 0:
            completed = self.step(vm)
            vm.execute()
        return completed
        
    

def predictPosition(sx, sy, r2):
    """ Predict the coordinates after a Hohmann transfer from the current orbit to r2. """
    
    r1 = sqrt(sx**2 + sy**2)
    return (-r2 * sx/r1, -r2 * sy/r1)

def timeRequired(r1, r2):
    return pi * sqrt((r1+r2)**3/(8*mu))

def fuelRequired(r1,r2):
    return abs(dV1(r1,r2)) + abs(dV2(r1,r2))

def radiusFromTime(r1, t):
    cuberoot = lambda x: x**(1/3.0)
    return cuberoot((t/pi)**2 * 8 * mu) - r1

def integerTimeApprox(r1, r2):
    """ Returns a radius close to r2 that can be reached from r1 in integer time. """
    t = timeRequired(r1, r2)
    tint = round(t)
    return radiusFromTime(r1, tint)    