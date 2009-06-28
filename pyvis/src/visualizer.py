from __future__ import with_statement

import psyco
psyco.full()

import sys
import re

from threading import Thread	
from math import *
from random import *
import time

from vm import Hohmann, MeetGreet, Eccentric, ClearSkies, EarthRadius

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

global glPixel
glPixel = 1

#from OpenGLContext import testingcontext
#BaseContext, MainFunction = testingcontext.getInteractive()
#from OpenGLContext.arrays import array
#from OpenGLContext.scenegraph.text import glutfont
#from pyglet import image, font

name = 'OrbitVIS'

def circle(x,y,r,segments=22):
	glBegin(GL_LINE_LOOP)
	for i in range(segments):
		a = 2*3.1415/segments*i
		glVertex2f(x+r*cos(a),y+r*sin(a))
	glEnd()

def drawText( value, x,y,  windowHeight, windowWidth, step = 18 ):
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
	
	def __call__(self, vis):
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
		drawText("Step:%d\nFuel:%d\nsx: %09f\nsy:%09f\nfuelstation:%d"\
				 %(vm.currentStep, vm.state.fuel,
				   x, y, fuel2),
				 vis.centerx-vis.windowW/2*glPixel,
				 vis.centery+(vis.windowW/2-20)*glPixel, 100, 100)
		#glPopMatrix();
		
				
class SolutionThread(Thread):
	def __init__(self, vm, solver):
		Thread.__init__(self)
		self.vm = vm
		self.solver = solver
		self.term = 0
		
	def run(self):
		while not self.term:
			
			self.vm.execute()
			
			if self.solver:
				self.solver.step()

			time.sleep(0.0000002+0.0000)
			score = self.vm.state.score
			type = self.vm.scenario
			if score != 0:
				self.solution = self.vm.getSolution()
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

		for drawer in self.drawers:
			drawer(self)

		if self.scaler:
			self.sx = self.sx*0.95
			self.sy = self.sy*0.95
		
		if self.zoomstate:
			self.sx = self.sx + self.sx*0.1 * self.zoomstate

		glutSwapBuffers()
