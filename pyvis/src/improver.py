from copy import deepcopy
from math import *
from numpy import array,dot,transpose
from numpy.linalg import solve

class ImproverFailure(Exception):
    pass

def leastSquares(a,c):
    a = array(a)
    c = array(c)
    c.shape = (len(c),1)
    
    aa = dot(a,transpose(a))
    ac = dot(a,c)
    
    x = solve(aa,ac)
    return list(x)

def traceCoords(vm,control,index,t1,t2):
    t0 = vm.state.time
    vm = vm.clone()
    result = []
    steps = vm.executeSteps(t1-t0,control)
    if steps < t1-t0:
        raise ImproverFailure()
    for i in range(t1,t2):
        result.append(vm.state.objects[index])
        steps = vm.executeSteps(1,control)
        if steps != 1:
            raise ImproverFailure()
    return result

def updateControls(controls,t,dvx,dvy):
    vx,vy = controls.get(t,(0,0))
    controls[t] = (vx+dvx,vy+dvy)
    
def calcBadness(vm,index,controls,t1,t2):
    targetTrace = traceCoords(vm,controls,index,t1,t2)
    baseTrace = traceCoords(vm,controls,0,t1,t2)
    badness = 0
    for p1,p2 in zip(baseTrace,targetTrace): 
        b = sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)
        badness = max(badness,b)
    return badness

def improveMeetAndGreet(vm,index,controls,freePoints,t1,t2,delta=0.0001):
    t0 = vm.state.time
    assert t0<t1 and t1<t2
    
    targetTrace = traceCoords(vm,controls,index,t1,t2)
    baseTrace = traceCoords(vm,controls,0,t1,t2)
    
    c = []
    for p1,p2 in zip(baseTrace,targetTrace): 
        c.append(p2[0]-p1[0])                
        c.append(p2[1]-p1[1])
    
    a = []
    
    deltas = [(delta,0),(0,delta)]
    
    for t in freePoints:
        for d in deltas:
            contr = deepcopy(controls)
            updateControls(contr,t,*d)
            trace = traceCoords(vm,contr,0,t1,t2)
            a.append([])
            for p1,p2 in zip(baseTrace,trace):
                a[-1].append(p2[0]-p1[0])                
                a[-1].append(p2[1]-p1[1])
    
    sol = leastSquares(a,c)
    sol = array(sol)
    sol.shape = (len(sol)//2,2)
    
    result = deepcopy(controls)
    for t,row in zip(freePoints,sol):
        for f,(dx,dy) in zip(row,deltas):
            updateControls(result,t,f*dx,f*dy)
    return result

def tryImprove(vm,index,controls,freePoints,t1,t2):
    badness = calcBadness(vm,index,controls,t1,t2)
    while badness > 950.0:
        attempts = []
        for delta in [0.0001,0.001,0.01,0.1]:
            try:
                delta = 0.001
                c = improveMeetAndGreet(vm,index,controls,freePoints,t1,t2,delta)
                newBadness = calcBadness(vm,index,c,t1,t2)
                attempts.append((newBadness,c))
            except ImproverFailure:
                pass
        if len(attempts) == 0:
            raise ImproverFailure("all improvement attempts crashed")
        attempts.sort()
        if attempts[0][0] >= badness:
            raise ImproverFailure("no actual improvements")
        print 'improvement from',badness,'to',attempts[0]
        badness = attempts[0][0]
        controls = c
    print "Succesfully improved to badness",badness
    return controls