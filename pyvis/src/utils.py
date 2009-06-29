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

def hohmannParameters(r1,r2):
    """return (dv1,dv2,interval)"""
    r1 = abs(r1)
    r2 = abs(r2)
    dv1 = sqrt(mu/r1)*(sqrt(2*r2/(r1+r2))-1)
    dv2 = sqrt(mu/r2)*(1-sqrt(2*r1/(r1+r2)))
    interval = int(round(periodByRadius(0.5*(r1+r2))/2))
    return dv1,dv2,interval

def performHohmann(hvm,t,r2):
    #return (hvm,controls,expectedTime)
    
    hvm = hvm.clone()
    hvm.executeSteps(t-hvm.state.time)
    
    s1 = hvm.state.cobjects[0]
    v1 = getObjCSpeeds(hvm)[0]
    rotDir = rotationDir(s1,v1)
    
    dv1,dv2,interval = hohmannParameters(s1,r2)
    
    c = {}
    c[t] = complToPair(dv1*s1/abs(s1)*rotDir)
    c[t+interval] = complToPair(-dv2*s1/abs(s1)*rotDir)
    
    return (hvm,c,t+interval)
    

def gravForce(cobj,cmoon=None):
    r = abs(cobj)
    if abs(r)<1.0:
        print 'warning: too close to earth'
        return 0
    f = -mu*cobj/(r*r*r)
    if cmoon is not None:
        s = cobj-cmoon
        r = abs(s)
        if r<1.0:
            return f
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
    for i in range(len(vm.state.cobjects)):
        o = vm.state.cobjects[i]
        o1 = vm1.state.cobjects[i]
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
    
def ensureCircularOrbit(hvm):
    hvm = hvm.clone()
    speeds = getObjCSpeeds(hvm)        
    s = hvm.state.cobjects[0]
    v0 = speeds[0]
    v = (s/abs(s))*rotationDir(s,v0)*speedByRadius(s)
    hvm.executeSteps(1,{hvm.state.time:complToPair(v-v0)})
    return hvm

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
    print 'collecting history...',
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

def fuelUse(controls,t0=1):
    return sum(abs(complex(*c)) for t,c in controls.items() if t>=t0)