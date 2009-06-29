import psyco
psyco.full()

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from copy import deepcopy
from math import *
from pprint import pprint


from utils import *
from vminterface import createScenario,getSolution,HistoryVM
from improver import *

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
    [(0.4,0.7,0.7)]*10+
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
            #if i>=2 and i<2+12 and state.collected[i-2]:
            #    continue
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

    drawStates(decimateList(states,0.5))

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

def needCollect(vm,index):
    if vm.state.fuel < 4000:
        return index == 1 #hunger!
      
    if index == 1:
        return vm.state.fuel<5000
    elif index >= 2 and index < 2+12:
        return not vm.state.collected[index-2] and \
            vm.state.cobjects[index] != vm.state.cobjects[0] # because 12-th object is bullshit
    else:
        return False

def getSwitchings(vm,index,lookAhead=3000000):
    t0 = vm.state.time
    s1 = vm.state.cobjects[0]
    v1 = getObjCSpeeds(vm)[0]
    rotDir = rotationDir(s1,v1)
    omega1 = 2*pi/periodByRadius(s1)
    
    switchings = []
    prevShift = 1000
    for t,coords,speeds in history:
        if t<vm.state.time:
            continue
        if t>vm.state.time+lookAhead:
            continue
        
        s2 = coords[index]
        hohTime = hohmannParameters(s1,s2)[2]
        
        neededPos = -s2/abs(s2)*abs(s1)
        ourPos = s1*cmath.exp(omega1*(t-hohTime-t0)*rotDir)
        
        shift = cmath.phase(neededPos*ourPos.conjugate())
        if prevShift*shift<0 and abs(prevShift)<1.5:
            passT = (prevT*shift-t*prevShift)/(shift-prevShift)
            swt = int(round(passT-hohTime))
            if swt >= vm.state.time:
                switchings.append((swt,abs(s2),index))
        prevShift = shift
        prevT = t
    return switchings

def tryCollect(hvm,switch,timeCost):
    t,r2,index = switch
    
    if r2>1e9:
        return (-1e20,None,None,None,None)
    
    hvm,controls,expectedTime = performHohmann(hvm,t,r2)
    
    fu = fuelUse(controls)
    
    if fu > hvm.state.fuel+20:
        return (-1e20,None,None,None,None)
    
    score = -75.0/24e6*(expectedTime-t)*timeCost-25*fu/hvm.state.startfuel
    
    if index >= 2 and index < 12+2:
        score += 75*(1.0/12)
        
    if hvm.state.fuel < 5000 and index == 1:
        score += 100500 # check fueller first
    
    return (8*score,hvm,controls,index,expectedTime)
    

def collect(hvm,timeCost,maxResults=1):
    hvm = hvm.clone()
    hvm = ensureCircularOrbit(hvm)
    
    switchings = []
    for index in range(2,12+2):
        if needCollect(hvm,index):
            switchings += getSwitchings(hvm.vm,index,lookAhead=500000)
#    print 'got',len(switchings),'switchings'
    switchings.sort()
    switchings = switchings[:10]
    
    if hvm.state.fuel < 9000:
        fuelSwitchings = getSwitchings(hvm.vm,1,lookAhead=500000)
        fuelSwitchings.sort()
        switchings += fuelSwitchings[:1] # have at least one emergency switches! 
    
    if len(switchings)>0:
        # factor out common part of execution for all tries
        minT = min(sw[0] for sw in switchings)
        hvm.executeSteps(minT-hvm.state.time) 
    
    tries = [tryCollect(hvm,sw,timeCost) for sw in switchings]
    
    
    tries.sort()
    tries.reverse()
    
    result = []
    
    for tr in tries:
        sc,hvm,controls,index,expectedTime = tr
        
        if sc < -1e15:
            continue
        
        try:
            controls = tryImprove(hvm.vm,index,controls,
                                  [hvm.state.time],
                                  expectedTime,expectedTime+1)
        except ImproverFailure as e:
            print e
            
        hvm.executeSteps(expectedTime-hvm.state.time+1,controls)
        
        hvm.comment += " -> "+str(index)
        #print 'fuel remaining',hvm.state.fuel
        result.append(hvm)
        if len(result) == maxResults:
            break
    return result
bestHvm = None
def verify(hvm):
    global bestHvm
    score = hvm.vm.getApproxScore()
    if bestHvm is None or bestHvm.vm.getApproxScore()<score:
        print 'found better solution (%s, fuel=%s,%s)'%\
            (score,int(hvm.state.fuel),hvm.comment)
        bestHvm = hvm
        
def solve(hvm):
    print 'currently at',hvm.comment
    verify(hvm)
    unCollected = len([i for i in range(15) if needCollect(hvm,i)])
    for newHvm in collect(hvm,timeCost=unCollected,maxResults=branching):
        solve(newHvm)

def main():
    global branching
    branching = 1
    
    
    global winW,winH
    global states,scale
    
    
    global step
    global history
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(winW,winH)
    glutCreateWindow(name)
    
    glutDisplayFunc(display)
    glutReshapeFunc(resize)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)

    if len(sys.argv) == 2:
        scenario = int(sys.argv[1])
        noVis = True
    else:
        scenario = 4001
        noVis = False
        
    vm = createScenario('compiled','../../task/bin4.obf',scenario)
    vm0 = vm.clone()
    
    print 'fuel',vm.state.fuel
    
    
    step = 300
    maxTime = 2000000/10
    
    history = getHistory(vm,step,maxTime)[:maxTime//step]
    
    hvm = HistoryVM(vm)
    
    solve(hvm)
    
    controls = bestHvm.commands
    print 'final controls'
    pprint(sorted(controls.items()))
    
    endTime = bestHvm.state.time
    
    print 'best solution',bestHvm.comment
    print 'approx score',bestHvm.vm.getApproxScore()
    
    vm = vm0.clone()
    print 'evaluating score...'
    vm.executeSteps(2000000,controls)
    print 'collected',vm.state.collected
    print 'fuel =',vm.state.fuel
    print 'SCORE = ',vm.state.score
    
    with open('solutions/sol%s_%s'%(scenario,int(vm.state.score)),
              'wb') as fout:
        fout.write(getSolution(scenario,vm.state.time,controls))
    
    if noVis:
        sys.exit()
        
        
    vm = vm0.clone()
    states = []
    for i in range(1,endTime,100):
        states.append(deepcopy(vm.state))
        vm.executeSteps(100,controls)
    
        
    scale = max(sqrt(x*x+y*y) 
                for state in states 
                for x,y in state.objects)

    #scale = min(scale,5e7)
    
    glutMainLoop()

if __name__ == '__main__': 
    main()