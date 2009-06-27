from math import sqrt

dV1 = lambda r1, r2: sqrt(mu/r1) * (sqrt(2*r2/(r1+r2)) - 1)
dV2 = lambda r1, r2: sqrt(mu/r2) * (1 - sqrt(2*r1/(r1+r2)))

mu = 6.67428 * 6.0 * 10**13

class transfer:
    def __init__(self, vm, spin=0):
        
        # do the first step to get stats
        vm.execute()
        # get stats
        sx, sy = vm.stats.sx, vm.stats.sy
        self.r1 = sqrt(sx**2 + sy**2)
        self.r2 = vm.outPort[4]
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
                self.spin = 1 if sx * self.syInit - sy * self.sxInit < 0 else -1

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
