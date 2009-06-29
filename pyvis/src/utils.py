from math import *
from copy import copy,deepcopy
import cmath

G = 6.67428e-11
earthMass = 6e24    
moonMass = 7.347e22
mu = G*earthMass
moonMu = G*moonMass

def periodByRadius(r):
    r = abs(r)
    return 2*pi*sqrt((r*r*r)/mu)

def speedByRadius(r):
    r = abs(r)
    return r*(2*pi)/periodByRadius(r)

def hohmann(r1,r2):
    """return (dv1,dv2,interval)"""
    r1 = abs(r1)
    r2 = abs(r2)
    dv1 = sqrt(mu/r1)*(sqrt(2*r2/(r1+r2))-1)
    dv2 = sqrt(mu/r2)*(1-sqrt(2*r1/(r1+r2)))
    interval = int(round(periodByRadius(0.5*(r1+r2))/2))
    return dv1,dv2,interval

def performHohmann(vm,controls,t,r2):
    #return (vm,controls,expectedTime)
    
    vm = vm.clone()
    vm.executeSteps(t-vm.state.time,controls)
    
    s1 = vm.state.cobjects[0]
    v1 = getObjCSpeeds(vm)[0]
    rotDir = rotationDir(s1,v1)
    
    dv1,dv2,interval = hohmann(s1,r2)
    
    c = {}
    c[t] = complToPair(dv1*s1/abs(s1)*rotDir)
    c[t+interval] = complToPair(-dv2*s1/abs(s1)*rotDir)
    
    controls = combineControls(controls,c)
    return (vm,controls,t+interval)
    

def gravForce(cobj,cmoon=None):
    r = abs(cobj)
    if abs(r)<1.0:
        print 'warning: too close to earth'
        return 0
    f = -mu*cobj/(r*r*r)
    if cmoon is not None:
        s = cobj-moon
        r = abs(s)
        f -= moonMu*s/(r*r*r) 
    return f
    
    
def complToPair(a):
    return a.real,a.imag

def getObjCSpeeds(vm):
    vm1 = vm.clone()
    if vm1.executeSteps(1) == 0:
        return [0 for o in vm.state.cobjects]
    speeds = []
    if len(vm.state.cobjects)>10:
        moon = vm.state.cobjects[-1]
    else:
        moon = None
    for o,o1 in zip(vm.state.cobjects,vm1.state.cobjects):
        speeds.append(o1-o-0.5*gravForce(o,moon))
    return speeds

def isCCW(s,v):
    assert abs(s)>0.001
    return (v/s).imag>0

def rotationDir(s,v):
    assert abs(s)>0.001
    if (v/s).imag > 0:
        return 1j
    else:
        return -1j
    
def ensureCircularOrbit(vm):
    speeds = getObjCSpeeds(vm)        
    s = vm.state.cobjects[0]
    v0 = speeds[0]
    v = (s/abs(s))*rotationDir(s,v0)*speedByRadius(s)
    return {1:complToPair(v-v0)}    

def combineControls(controls1,controls2):
    result = deepcopy(controls1)
    for t,(dx,dy) in controls2.items():    
        if t not in result:
            result[t] = dx,dy
        else:
            qx,qy = result[t]
            result[t] = qx+dx,qy+dy
    return result
            
def getHistory(vm,step,maxTime=30000000):
    print 'collecting hisotry...',
    vm = vm.clone()
    n = len(vm.state.cobjects)
    history = []
    while vm.state.score == 0.0 and vm.state.time<maxTime:
        history.append((vm.state.time,
                        copy(vm.state.cobjects),
                        getObjCSpeeds(vm)))
        vm.executeSteps(step,{})
    print 'ok'
    return history

def fuelUse(controls):
    return sum(abs(complex(*c)) for c in controls.values())