import psyco
psyco.full()

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from copy import deepcopy
from math import *

from vm import *
from history import History
from simulator import Simulator

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
    [(0.7,0.7,0.7)]*11+
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
    glScalef(float(winH)/winW,1,1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glOrtho(-scale,scale,-scale,scale,-1,1)
    
    glColor3f(0,0.3,0.6)
    circle(0,0,6.357e06)

    glPointSize(3)
    for state in decimateList(history.states,rate=0.01):
        drawState(state)
        
#    glPointSize(1)
#    i = 0
#    for state in decimateList(simStates):
#        drawState(state)
#        i += 1
    drawStates(decimateList(simStates))

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
    global history,vm,scale
    global simStates
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(winW,winH)
    glutCreateWindow(name)
    
    glutDisplayFunc(display)
    glutReshapeFunc(resize)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    
    assert len(sys.argv) == 3,"specify obf and scenario"
    vm = createScenario(sys.argv[1],int(sys.argv[2]))
    history = History(vm,lookAhead=10000)
    
    simulator = Simulator(history.states[0],history.states[1:2])
    simStates = []
    maxErr = 0
    for i in range(5000):
        s1 = simulator.state
        s2 = history.getStateByTime(s1.time)
        if s2 is not None:
            print '(r-k):   ',s1
            print '(exact):',s2
            errs = State.dists(s1,s2)
            print 'errors =',errs
            err = max(errs)
            print 'error =',err
            maxErr = max(maxErr,err)
            print
        simStates.append(deepcopy(simulator.state))
        #simulator.simulate(1)
        simulator.rungeKutta(100)
    print 'Maximum error over simulation:',maxErr
    
    scale = max(sqrt(x*x+y*y) 
                for state in history.states 
                for x,y in state.objects)
    scale = max(scale,1e7)
    #scale += 1e3
    
    
    glutMainLoop()

if __name__ == '__main__': 
    main()