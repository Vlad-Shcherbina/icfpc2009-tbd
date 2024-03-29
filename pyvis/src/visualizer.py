from __future__ import with_statement

import psyco
psyco.full()

import sys
import re
import time
from math import *
from random import *
from copy import deepcopy
from threading import Thread	

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

#from vm import Hohmann, MeetGreet, Eccentric, ClearSkies, EarthRadius
from simulator import Simulator

glPixel = 1

Hohmann = range(1001,1005)
MeetGreet = range(2001,2005)
Eccentric = range(3001,3005)
ClearSkies = range(4001,4005)

EarthRadius = 6.357e6

#from OpenGLContext import testingcontext
#BaseContext, MainFunction = testingcontext.getInteractive()
#from OpenGLContext.arrays import array
#from OpenGLContext.scenegraph.text import glutfont
#from pyglet import image, font

name = 'OrbitVIS'

def circle(x,y,r,segments=30):
	glBegin(GL_LINE_LOOP)
	for i in range(segments):
		a = 2*3.1415/segments*i
		glVertex2f(x+r*cos(a),y+r*sin(a))
	glEnd()

factor = 100

keyMapping = { 
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
    }

def keyboardHandler(vis, key, x, y):
    vm = vis.vm
    if keyMapping.has_key(key):
    	print keyMapping[key]
        vm.changeSpeed(keyMapping[key][0]*factor, keyMapping[key][1]*factor)



class StatsDrawer:
	def __init__(self):
		pass
	
	def draw(self, vis):
		vm = vis.vm
		#glPushMatrix();
		#glMatrixMode(GL_PROJECTION);
		#glOrtho(0.0, 100, 0.0, 100, -1.0, 1.0)
		#glLoadIdentity();
		glColor3f(1,1,1)
		
		fuel2 = 0
		if vm.scenario in ClearSkies:
			fuel2 = vm.state.fuel2

		x, y = vm.state.objects[0]
		vis.drawText("Step:%d\nFuel:%d\nsx: %09f\nsy:%09f\nfuelstation:%d"\
				 %(vm.currentStep, vm.state.fuel,
				   x, y, fuel2),
				 0, 20, 100, 100)
		#glPopMatrix();

from solvers.orbital import *

class RadiusDrawer:
	def __init__(self):
		pass
	
	def draw(self, vis):
		vm = vis.vm

		if len(vm.history) < 3:
			return

		for i in range(len(vm.state.objects)):
			curpos = vm.state.objects[i]
			prevpos = vm.history[-2].objects[i]
			vd = vDiff(curpos, prevpos)
			nextpos = vSum(curpos, vMul(vd,10e6/vLen(vd)))

			cradius = vLen(curpos)
			
			glPushMatrix()
			glColor3f(0.5,0.5,0.5)
			circle(0, 0, cradius)
			glBegin(GL_LINE_LOOP)
			glVertex2f(*curpos)
			glVertex2f(*nextpos)
			glEnd()	
			glPopMatrix()


class PredictDrawer:
	def __init__(self):
		pass
	
	def draw(self, vis):
		vm = vis.vm
		
		#history = History(vm,lookAhead=10)
		#simulator = Simulator(history.states[0],history.states[1:2])

		if len(vm.history) < 3:
			return
		
		simulator = Simulator(vm.history[0], vm.history[1:2])
		simStates = []
		maxErr = 0
		for i in range(10):
		    simStates.append(deepcopy(simulator.state))
		    #simulator.simulate(1)
		    simulator.rungeKutta(1000)
		glColor3f(0.9,0.5,0.5)
		for i in reversed(range(len(simStates[0].objects))):
			glBegin(GL_LINE_STRIP)
			for state in simStates:
			    x,y = state.objects[i]
			    glVertex2f(x,y)
			glEnd()
        
		
		
				
class SolutionThread(Thread):
	def __init__(self, vm, solver):
		Thread.__init__(self)
		self.vm = vm
		self.solver = solver
		self.term = 0
		
		
	def run(self):
		vm = self.vm
		vm.history = []
		while not self.term:
			vm.execute()
			
			if self.solver:
				self.solver.step()
			
			vm.history.append(deepcopy(vm.state))
			if (len(vm.history) > 5):
				vm.history = vm.history[1:]

			time.sleep(0.0000002+0.0000)
			score = vm.state.score
			type = vm.scenario
			if score != 0:
				#break
				self.solution = vm.getSolution()
				fname = "solutions/sol_%04d_%06d_%s.osf"%(type, score,
			                re.sub(r'[\s:]', "_", time.ctime()))
				with open(fname,'wb') as fout:
				    fout.write(self.solution)
				print "stored into "+ fname
				break
		return

	def terminate(self):
		self.term = 1
		self.join
		return
	
	def _idle(self):
		1
		#
					
				
				
class Visualizer(Thread):
	def __init__(self, vm, solver, scaler = 0, keyHandler = None, mouseHandler = None):
		Thread.__init__(self)
		self.terminate = False
		self.drawers = []
		
		self.vm = vm
		self.solver = solver
		
		self.keyHandler = keyHandler
		self.mouseHandler = mouseHandler
		
		self.sx = 0
		self.sy = 0
		self.centerx = 0
		self.centery = 0
		
		self.mousex = 0
		self.mousey = 0
		
		self.zoomstate = 0
		self.manualzoom = 0
		self.sradius = EarthRadius/15

		""" if scaling back is required """
		self.scaler = scaler
		
		self.solutionThread = SolutionThread(vm, solver)
		
	def registerDrawer(self,drawer):
		self.drawers.append(drawer)
		
	def drawText(vis, value, x,y,  windowHeight, windowWidth, step = 18 ):
		"""Draw the given text at given 2D position in window
		"""
		#glMatrixMode(GL_PROJECTION);
		# For some reason the GL_PROJECTION_MATRIX is overflowing with a single push!
		# glPushMatrix()
		#matrix = glGetDouble( GL_PROJECTION_MATRIX )
		
		#glLoadIdentity();
		#glOrtho(0.0, windowHeight or 32, 0.0, windowWidth or 32, -1.0, 1.0)
		#glMatrixMode(GL_MODELVIEW);
		#glPushMatrix();
		#glLoadIdentity();
		x = int(vis.centerx-(vis.windowW/2+x)*glPixel)
		y = int(vis.centery+(vis.windowH/2-y)*glPixel)
					 
		glRasterPos2i(int(x), int(y));
		lines = 1
	##	import pdb
	##	pdb.set_trace()
		for character in value:
			if character == '\n':
				glRasterPos2i(x, y-(lines*step*glPixel))
				lines = lines+1
			else:
				glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character));
		#glPopMatrix();
		#glMatrixMode(GL_PROJECTION);
		# For some reason the GL_PROJECTION_MATRIX is overflowing with a single push!
		# glPopMatrix();
		#glLoadMatrixd( matrix ) # should have un-decorated alias for this...
		
		#glMatrixMode(GL_MODELVIEW);

	
	def earth(self):
		glColor3f(0,1,0)
		circle(0, 0, EarthRadius)

	def moon(self, x, y):
		self.relocate(x, y)
		
		glPushMatrix()
		glTranslatef(x, y, 0)
		glColor3f(1,1,1)
		circle(0, 0, EarthRadius/5)
		glPopMatrix()

	def satellite(self, x, y):
		self.relocate(x, y)

		glPushMatrix()
		glTranslatef(x,y,0)
		glColor3f(1,0,0)
		circle(0, 0, self.sradius)
		glPopMatrix()
	
	def satellite1(self, x, y):
		self.relocate(x, y)

		glPushMatrix()
		glTranslatef(x,y,0)
		glColor3f(1,1,0)
		circle(0, 0, self.sradius*0.5)
		glPopMatrix()
	
	def fuelstation(self, x, y, fuel):
		self.relocate(x, y)

		glPushMatrix()
		glTranslatef(x,y,0)
		glColor3f(1,0,1)
		circle(0, 0, self.sradius)
		circle(0, 0, self.sradius*1.1)		
		glPopMatrix()

	def relocate(self, x, y):

		if self.manualzoom:
			return
		   
		if self.lastmax < abs(x)*1.1:
			self.lastmax = abs(x)*1.1
		if self.lastmax < abs(y)*1.1:
			self.lastmax = abs(y)*1.1
		
		if self.sx < self.lastmax:
			self.sx = self.lastmax
		if self.sy < self.lastmax:
			self.sy = self.lastmax

	def run(self):
		glutInit([])
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
		
		self.windowW = self.windowH = 700
		glutInitWindowSize(self.windowW,self.windowH)

		self.window = glutCreateWindow(name)
#		self.font = glutfont.GLUTFontProvider.get( FontStyle( family=["Arial","SANS"]))
#		glEnable(GL_DEPTH_TEST)

		glClearColor(0.,0.,0.,1.)
		glutDisplayFunc(self.display)
		glutIdleFunc(self._idle)
		if (self.keyHandler):
			glutKeyboardFunc(self._keyHandler)
		
		glutMouseFunc(self._mouseHandler)
		glutMotionFunc(self._motionHandler)

		# start!
		self.solutionThread.start()

		glutMainLoop()
		
	def _keyHandler(self, key, x, y):
		if self.keyHandler is not None:
			self.keyHandler(self,key,x,y)
	
	
	def _mouseHandler(self,button,state,x,y):
		if button == 0 and state == GLUT_DOWN:
			self.zoomstate = -1
		if button == 0 and state == GLUT_UP:
			self.zoomstate = 0

		if button == 2 and state == GLUT_DOWN:
			self.zoomstate = 1
		if button == 2 and state == GLUT_UP:
			self.zoomstate = 0

		if button == 1 and state == GLUT_DOWN:
			self.mousex = x
			self.mousey = y
		
		self.manualzoom = 1
	
		if self.mouseHandler is not None:
			self.mouseHandler(button,x,y)
	
	def _motionHandler(self, x, y):
		if self.zoomstate == 0:
			self.centerx = self.centerx - (x-self.mousex)*glPixel
			self.centery = self.centery + (y-self.mousey)*glPixel
			print "%d %d %d %d"%(x, y, self.mousex, self.mousey)
			self.mousex = x
			self.mousey = y
		pass
	
	def _idle(self):
		# because it is not a message handler
		
		if self.terminate:
			if self.window:
				glutDestroyWindow(self.window)
				self.window = None
			self.solutionThread.terminate()
			self.vm.terminate()
			return
		#time.sleep(0.02)
		glutPostRedisplay()


	def display(self):

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		
		self.lastmax = 0
		self.relocate(EarthRadius, EarthRadius)
		
		glOrtho(-self.sx+self.centerx,
				self.sx+self.centerx,
				-self.sx+self.centery,
				self.sx+self.centery, -10,10)
		
		global glPixel
		glPixel = int(self.sx/self.windowW*2)
		
		glMatrixMode(GL_MODELVIEW)

		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


		vm = self.vm
		objects = vm.state.objects
		
		# earth
		self.earth()
		
		# self
		self.satellite(objects[0][0], objects[0][1])
		
		if vm.scenario in Hohmann:
			pass
		
		elif vm.scenario in MeetGreet or vm.scenario in Eccentric:
			self.satellite1(objects[1][0], objects[1][1])
			pass
		
		elif vm.scenario in ClearSkies:
			
			self.fuelstation(objects[1][0], objects[1][1], vm.state.fuel2)

			#for c in range(12):
			#	self.satellite1(objects[2+c][0], objects[2+c][1])

			self.moon(vm.state.moon[0], vm.state.moon[1])	
			pass

		try:
			for drawer in self.drawers:
				drawer.draw(self)
		except:
			pass

		if self.scaler:
			self.sx = self.sx*0.95
			self.sy = self.sy*0.95
		
		if self.zoomstate:
			self.sx = self.sx + self.sx*0.1 * self.zoomstate

		glutSwapBuffers()
