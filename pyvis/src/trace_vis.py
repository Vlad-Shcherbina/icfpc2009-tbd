import psyco
psyco.full()

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from copy import deepcopy
from math import *


from utils import *

from vminterface import createScenario,getSolution

from compiled_vm import CompiledVMConstructor
from python_vm import PythonVMConstructor 
vmctr = CompiledVMConstructor


name = 'pyglut template'

winW = 700
winH = 700

def circle(x,y,r,segments=22):
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2*pi/segments*i
        glVertex2f(x+r*cos(a),y+r*sin(a))
    glEnd()

standartColorScheme = (
    [(1,1,1),(0,1,0)]+
    [(1,0.5,0.5)]+
    [(0.7,0.7,0.7)]*9+
    [(1,0,0)]*2+
    [(1,1,0)] # moon 
)

def drawState(state,colorScheme=standartColorScheme):
    glBegin(GL_POINTS)
    for i in reversed(range(len(state.objects))):
        x,y = state.objects[i]
        glColor3f(*colorScheme[i])
        glVertex2f(x,y)
    glEnd()
   
def drawStates(states,colorScheme=standartColorScheme):
    if len(states)==0:
        return
    for i in reversed(range(len(states[0].objects))):
        glColor3f(*colorScheme[i])
        glBegin(GL_LINE_STRIP)
        for state in states:
            x,y = state.objects[i]
            glVertex2f(x,y)
        glEnd()
        
def decimateList(list,rate=0.1):
    result = []
    x = 1
    for e in list:
        x += rate
        if x >= 1:
            x -= 1
            result.append(e)
    return result

def display():
    global winW,winH
    glViewport(0,0,winW,winH)

    glClearColor(0.,0.,0.,1.)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glScalef(float(winH)/(winW+0.1),1,1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glOrtho(-scale,scale,-scale,scale,-1,1)
    
    glColor3f(0,0.3,0.6)
    circle(0,0,6.357e06)

    drawStates(decimateList(states))

    glutSwapBuffers()
    glutPostRedisplay()

def idle():
    glutPostRedisplay()

def keyboard(key,x,y):
    if key == chr(27): #esc
        sys.exit()

def resize(w,h):
    global winW,winH
    winW,winH = w,h
    
#############################3



def main():
    global winW,winH
    global states,scale
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(winW,winH)
    glutCreateWindow(name)
    
    glutDisplayFunc(display)
    glutReshapeFunc(resize)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    
    assert len(sys.argv) == 3,"specify obf and scenario"
    vm = createScenario(vmctr,sys.argv[1],int(sys.argv[2]))
    print vm.state.fuel
    

    r1 = abs(complex(*vm.state.objects[0]))
    r2 = abs(complex(*vm.state.objects[1]))
    print 'radii',r1,r2
    

    
    dv1 = sqrt(mu/r1)*(sqrt(2*r2/(r1+r2))-1)
    dv2 = sqrt(mu/r2)*(1-sqrt(2*r1/(r1+r2)))
    hohTime = periodByRadius(0.5*(r1+r2))/2
    print 'hoh time',hohTime
    
    controls = {}
    controls[1] = (0,-dv1)
    controls[int(hohTime)] = (0,dv2)

    states = []
    for i in range(7000):
        states.append(deepcopy(vm.state))
        vm.executeSteps(1,controls)
    
        
    scale = max(sqrt(x*x+y*y) 
                for state in states 
                for x,y in state.objects)
    #scale = max(scale,1e7)
    
    glutMainLoop()

if __name__ == '__main__': 
    main()