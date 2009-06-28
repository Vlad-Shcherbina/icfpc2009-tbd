from copy import deepcopy
from math import *
from numpy import array,dot,transpose
from numpy.linalg import solve

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
    for i in range(t0,t2):
        assert vm.state.time == i
        if i in control:
            vm.changeSpeed(*control[i]) 
        if i >= t1:
            for q in range(2):
                result.append(vm.state.objects[index])
        vm.execute()
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

def improveMeetAndGreet(vm,index,controls,freePoints,t1,t2):
    targetTrace = traceCoords(vm,controls,index,t1,t2)
    baseTrace = traceCoords(vm,controls,0,t1,t2)
    
    c = []
    badness = 0
    for p1,p2 in zip(baseTrace,targetTrace): 
        c.append(p2[0]-p1[0])                
        c.append(p2[1]-p1[1])
        b = sqrt(c[-1]**2+c[-2]**2)
        badness = max(badness,b)
    print 'badness',badness
    
    a = []
    
    deltas = [(0.0001,0),(0,0.0001)]
    
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
        