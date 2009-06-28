from math import *

G = 6.67428e-11
earthMass = 6e24    
mu = G*earthMass

def periodByRadius(r):
    return 2*pi*sqrt((r*r*r)/mu)

def hohmann(r1,r2):
    """return (dv1,dv2,interval)"""
    dv1 = sqrt(mu/r1)*(sqrt(2*r2/(r1+r2))-1)
    dv2 = sqrt(mu/r2)*(1-sqrt(2*r1/(r1+r2)))
    interval = periodByRadius(0.5*(r1+r2))/2
    return dv1,dv2,interval
    
def complToPair(a):
    return a.real,a.imag