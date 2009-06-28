from math import sqrt, sin, cos, atan2

mu = 6.67428 * 6.0 * 10**13

angular = lambda r: sqrt(mu/r**3)

def newPosition(x, y, spin, t):
    r = sqrt(x**2 + y**2)
    angle = spin * angular(r) * t
    s, c = sin(angle), cos(angle)
    return (c * x - s * y, s * x + c * y)

def getSpin(x1, y1, x2, y2):
    return 1 if x2 * y1 - y2 * x1 < 0 else -1


def vSum(v1, v2):
    return (v1[0]+v2[0], v1[1]+v2[1])

def vDiff(v1, v2):
    return(v1[0]-v2[0], v1[1]-v2[1])

def vMul(v1, m):
    return (v1[0]*m, v1[1]*m)

def vLen(v1):
    return sqrt(v1[0]**2 + v1[1]**2)
    
def vAngle(v):
    return atan2(v[1], v[0])
