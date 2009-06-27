from copy import deepcopy
from math import *

class Object(object):
    __slots__ = ('x','y','vx','vy')
    
G = 6.67428e-11
earthMass = 6e24
moonMass = 7.347e22

def gravTo(x,y,mass):
    d = sqrt(x*x+y*y)
    if d < 1:
        return 0,0
    dx = x/d
    dy = y/d
    a = G*mass/(x*x+y*y)
    return a*dx,a*dy

def deriv(objects):
    result = []
    for obj in objects:
        d = Object()
        d.x = obj.vx
        d.y = obj.vy
        d.vx,d.vy = gravTo(-obj.x,-obj.y,earthMass)
        if len(objects) > 10: # have moon
            max,may = gravTo(objects[-1].x-obj.x,
                             objects[-1].y-obj.y,
                             moonMass)
            d.vx += max
            d.vy += may
        result.append(d)
    return result

def advance(objs,dobjs,dt):
    for obj,d in zip(objs,dobjs):
        obj.x += d.x*dt
        obj.y += d.y*dt
        obj.vx += d.vx*dt
        obj.vy += d.vy*dt

class Simulator(object):
    def __init__(self,state,nextState):
        self.objects = []
        for o in state.objects:
            obj = Object()
            obj.x = o[0]
            obj.y = o[1]
            obj.vx = 0
            obj.vy = 0
            self.objects.append(obj)
        self.state = deepcopy(state)
        self.time = state.time
        
        #calcForces(self.objects)
        d = deriv(self.objects)
        for i,obj in enumerate(self.objects):
            obj.vx = nextState.objects[i][0]-0.5*d[i].vx-state.objects[i][0]
            obj.vy = nextState.objects[i][1]-0.5*d[i].vy-state.objects[i][1]
        
            
    def simulate(self,dt):
        d = deriv(self.objects)
        #advance(self.objects,d,dt)
        for obj,dobj in zip(self.objects,d):
            obj.x += (obj.vx+0.5*dobj.vx*dt)*dt
            obj.y += (obj.vy+0.5*dobj.vy*dt)*dt
            obj.vx += dobj.vx*dt
            obj.vy += dobj.vy*dt
        self.time += dt
        self.updateState()
        
    def rungeKutta(self,dt):
        y0 = deepcopy(self.objects)
        k1 = deriv(y0)
        y1 = deepcopy(y0)
        advance(y1,k1,0.5*dt)
        k2 = deriv(y1)
        y2 = deepcopy(y0)
        advance(y2,k2,0.5*dt)
        k3 = deriv(y2)
        y3 = deepcopy(y0)
        advance(y3,k3,dt)
        k4 = deriv(y3)
        advance(self.objects,k1,1.0/6*dt)
        advance(self.objects,k2,2.0/6*dt)
        advance(self.objects,k3,2.0/6*dt)
        advance(self.objects,k4,1.0/6*dt)
        self.time += dt
        self.updateState()
        
            
    def updateState(self):
        self.state.time = self.time
        for i,obj in enumerate(self.objects):
            self.state.objects[i] = obj.x,obj.y
