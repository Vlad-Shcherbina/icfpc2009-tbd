from math import sqrt, pi
from orbital import mu, getSpin

dV1 = lambda r1, r2: sqrt(mu/r1) * (sqrt(2*r2/(r1+r2)) - 1)
dV2 = lambda r1, r2: sqrt(mu/r2) * (1 - sqrt(2*r1/(r1+r2)))


#### DEPRECATED
class transfer:
    def __init__(self, r1, r2, spin=0):
        assert 0, "DEPRECATED: Use the hohmann_transfer.performTransfer function"
        self.r1 = r1
        self.r2 = r2
        self.spin = spin
        assert spin in (-1,0,1)
        if spin == 0:
            self.state = 0
        else:
            self.state = 1

    def step(self, vm):
        sx, sy = vm.state.objects[0]
        r = vm.state.r

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

            vm.changeSpeed(*firstPulse(self.r1, self.r2, sx, sy, self.spin))

            self.timeLeft = int(round(timeRequired(self.r1, self.r2)))
            self.state = 2
            return 0

        elif self.state == 2:
            # wait for the transfer to be over, then make the second pulse

            self.timeLeft -= 1
            
            if self.timeLeft == 0:
                vm.changeSpeed(*secondPulse(self.r1, self.r2, sx, sy, self.spin))
                self.state = 3
                return self.spin
            else:
                return 0
            
        elif self.state == 3:
            return self.spin
    
    def performTransfer(self, vm):
        completed = 0
        while vm.state.score == 0.0 and completed == 0:
            completed = self.step(vm)
            vm.execute()
        return completed




def performTransfer(vm, r2, spin=0):
    if spin == 0: spin = obtainSpin(vm)
    x, y = vm.state.objects[0]
    r1 = sqrt(x**2 + y**2)
    nsteps = int(round(timeRequired(r1, r2)))
    vm.executeSteps(nsteps, {vm.state.time: firstPulse(r1, r2, x, y, spin)})
    x, y = vm.state.objects[0]
    vm.executeSteps(1, {vm.state.time: secondPulse(r1, r2, x, y, spin)})
        

def firstPulse(r1, r2, x, y, spin):
    dV = spin * dV1(r1, r2)
    dVx = -y * dV / r1
    dVy =  x * dV / r1
    return (dVx, dVy)
    
def secondPulse(r1, r2, x, y, spin):
    """ (x,y) is the position at the end of the jump """
    dV = spin * dV2(r1, r2)
    dVx = -y * dV / r2
    dVy = x * dV / r2
    return (dVx, dVy)

def obtainSpin(vm):
    x1, y1 = vm.state.objects[0]
    vm.executeSteps(1, {})
    x2, y2 = vm.state.objects[0]
    return getSpin(x1, y1, x2, y2)

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
    return abs(cuberoot((t/pi)**2 * 8 * mu) - r1)

def integerTimeApprox(r1, r2):
    """ Returns a radius close to r2 that can be reached from r1 in integer time. """
    t = timeRequired(r1, r2)
    tint = round(t)
    return radiusFromTime(r1, tint)



# the following are currently not used as the error has proven to be too large

def secondPulseX(r1, r2, x, y, spin):
    """ (x,y) is the position at the beginning of the jump """
    dV = spin * dV2(r1, r2)
    dVx = y * dV / r1
    dVy = -x * dV / r1
    return (dVx, dVy)
    
def transferControl(r1, r2, coords, spin, tstart=1):
    x, y = coords
    nsteps = int(round(timeRequired(r1, r2)))
    
    return (nsteps+2, {tstart: firstPulse(r1, r2, x, y, spin), \
                        tstart+nsteps: secondPulseX(r1, r2, x, y, spin)})
    