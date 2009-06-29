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

def circleIntersection(circle1, circle2):
    # http://2000clicks.com/mathhelp/GeometryConicSectionCircleIntersection.htm
    xA, yA, rA = circle1
    xB, yB, rB = circle2
    cA, cB = (xA, yA), (xB, yB)
    
    d = vLen(vDiff(cA, cB))
    K = 0.25 * sqrt(((rA+rB)**2-d**2)*(d**2-(rA-rB)**2))
    
    firstTerm = vMul(vSum(vSum(cB,cA), vMul(vDiff(cB, cA), (rA**2 - rB**2)/d**2)), 0.5)
    secondTerm = vMul((yB - yA, xA - xB), 2*K/d**2)
    
    return (vSum(firstTerm, secondTerm), vDiff(firstTerm, secondTerm))

    
    
    
    