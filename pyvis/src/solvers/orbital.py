from math import sqrt, sin, cos

mu = 6.67428 * 6.0 * 10**13

angular = lambda r: sqrt(mu/r**3)

def newPosition(x, y, spin, t):
    r = sqrt(x**2 + y**2)
    angle = spin * angular(r) * t
    s, c = sin(angle), cos(angle)
    return (c * x - s * y, s * x + c * y)

def getSpin(x1, y1, x2, y2):
    return 1 if x2 * y1 - y2 * x1 < 0 else -1