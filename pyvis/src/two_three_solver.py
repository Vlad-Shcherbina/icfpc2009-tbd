import psyco
psyco.full()

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from copy import deepcopy
from math import *
from pprint import pprint


from vminterface import createScenario,getSolution
from improver import *
from utils_for_two_three import *

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

def tryMeetGreet(vm,controls,switch):
    print '.',
    t,r2,index = switch
    
    if r2>1e9:
        return (-1e10,None,None,None)
    
    vm,controls,expectedTime = performHohmann(vm,controls,t,r2)
    
    vm2 = vm.clone()
    vm2.executeSteps(expectedTime+1-vm2.state.time,controls)
    speeds = getObjCSpeeds(vm2)
    syncSpeeds = {expectedTime:complToPair(speeds[index]-speeds[0])}
    controls = combineControls(controls,syncSpeeds)
    
    score = 25+45*(1-fuelUse(controls)/50000.0)+30-log((expectedTime+900)/1000,2)
    
    if fuelUse(controls)>50000:
        return (-1e10,None,None,None)
    
#    print 'score estimate',score*4
    return (4*score,vm,controls,expectedTime)
    
    

def main(task, scenario):
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

    vm = createScenario('compiled', task, scenario)
    print 'fuel',vm.state.fuel

    if True or scenario == 3003:
        step,maxTime = 500,1000000
    else:
        step,maxTime = 100,200000
    
    t0 = vm.state.time
    s1 = vm.state.cobjects[0]
    v1 = getObjCSpeeds(vm)[0]
    rotDir = rotationDir(s1,v1)
    omega1 = 2*pi/periodByRadius(s1)
    
    controls = ensureCircularOrbit(vm)
    
    history = getHistory(vm,step,maxTime)[:maxTime//step]
    
    switchings = []
    index = 1
    prevShift = 1000
    for t,coords,speeds in history:
        
        s2 = coords[index]
        hohTime = hohmann(s1,s2)[2]
        
        neededPos = -s2/abs(s2)*abs(s1)
        ourPos = s1*cmath.exp(omega1*(t-hohTime-t0)*rotDir)
        
        shift = cmath.phase(neededPos*ourPos.conjugate())
        if prevShift*shift<0 and abs(prevShift)<1.5:
            passT = (prevT*shift-t*prevShift)/(shift-prevShift)
            #print '***',passT
            swt = int(round(passT-hohTime))
            if swt>=vm.state.time:
                switchings.append((swt,abs(s2),index))
        #print t,shift
        prevShift = shift
        prevT = t

    #pprint(switchings)
    print 'got',len(switchings),'switchings'
    tries = [tryMeetGreet(vm,controls,sw) for sw in switchings]
    print
    tries.sort()
    tries.reverse()
    #pprint(tries)
    sc,vm1,controls,expectedTime = tries[0]
    assert sc>0
    
    print 'score estimate',sc
    
    try:
        controls = tryImprove(vm1,index,controls,
                              [vm1.state.time,expectedTime],
                              expectedTime,expectedTime+900)
    except ImproverFailure as e:
        print e
    
    #print controls
    vm0 = vm.clone()
    vm.executeSteps(1000000,controls)
    print 'fuel =',vm.state.fuel
    print 'SCORE = ',vm.state.score
    
    with open('solutions/hoh_sol%s_%s'%(scenario,int(vm.state.score)),
              'wb') as fout:
        fout.write(getSolution(scenario,vm.state.time,controls))
    
    
    vm = vm0
    states = []
    for i in range(1,expectedTime+900,20):
        states.append(deepcopy(vm.state))
        vm.executeSteps(20,controls)
    
        
    scale = max(sqrt(x*x+y*y) 
                for state in states 
                for x,y in state.objects)

    #scale = max(scale,1e7)
    
    #glutMainLoop()

if __name__ == '__main__':
#    for i in range(4): 
#        main('../../task/bin3.obf', 3001.0 + i)
    for i in range(4): 
        main('../../task/bin3.obf', 3001.0 + i)