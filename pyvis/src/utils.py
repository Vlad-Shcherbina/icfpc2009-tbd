from math import *

G = 6.67428e-11
earthMass = 6e24    
mu = G*earthMass

def periodByRadius(r):
    return 2*pi*sqrt((r*r*r)/mu)